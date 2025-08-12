import os, time, psycopg2, csv                           # stdlib (os/time/csv) e driver Postgres
from concurrent.futures import ThreadPoolExecutor, as_completed  # pool de threads + coleta por conclusão

DB_CONFIG = {                                            # parâmetros de conexão ao Postgres
    "dbname": "tpch", "user": "postgres", "password": "postgres",
    "host": "localhost", "port": 5432
}
QUERIES_DIR = r"tpch-kit\dbgen\queries_resolved"         # diretório com q1.sql .. q22.sql
N_QUERIES = 22                                           # total de queries TPC-H
N_ITERS = 100                                            # nº de rodadas (colunas 0..99 no CSV)
CSV_PATH = "tpch_timings_us.csv"                         # arquivo de saída com tempos (µs)

def ajustar_sql(sql: str) -> str:
    return (sql.replace("day (3)", "day")                # corrige 'interval ... day (3)' para PG
               .replace("limit -1", "")                  # remove 'limit -1' (incompatível)
               .replace(");\nlimit", "\nlimit")          # evita LIMIT após ';'
               .replace(";\nlimit", "\nlimit")           # idem
               .strip())                                 # tira espaços/quebras nas bordas

def executar_uma(i: int):
    caminho = os.path.join(QUERIES_DIR, f"q{i}.sql")     # monta caminho do arquivo da Qi
    with open(caminho, "r") as f:                        # abre o SQL da query
        sql = ajustar_sql(f.read())                      # lê e ajusta dialeto

    conn = psycopg2.connect(**DB_CONFIG)                 # abre conexão dedicada (por thread)
    conn.autocommit = True                               # sem transação explícita (só leitura)
    try:
        with conn.cursor() as cur:                       # cria cursor
            t0 = time.perf_counter_ns()                  # timestamp início (ns, monotônico)
            cur.execute(sql)                             # executa a query
            _ = cur.fetchall() if cur.description else None  # drena resultado se houver
            t1 = time.perf_counter_ns()                  # timestamp fim (ns)
            dur_us = (t1 - t0) // 1_000                  # converte duração para microssegundos
        return (i, dur_us)                               # retorna (id_query, duração_µs)
    finally:
        conn.close()                                     # garante fechar conexão

def executar_queries_concorrente(max_workers=8):
    futuros = {}                                         # mapa Future -> id da query
    with ThreadPoolExecutor(max_workers=max_workers) as executor:  # pool com N workers
        for i in range(1, N_QUERIES + 1):                # agenda Q1..Q22
            futuros[executor.submit(executar_uma, i)] = i
        resultados = []                                   # lista de (Qx, µs)
        for fut in as_completed(futuros):                 # coleta conforme cada future termina
            i, dur_us = fut.result()                      # obtém resultado da thread
            resultados.append((f"Q{i}", dur_us))          # armazena como ('Qn', tempo)
    return sorted(resultados, key=lambda x: int(x[0][1:]))# ordena por número da query

def main():
    header = ["Query"] + [str(i) for i in range(N_ITERS)] # cabeçalho CSV: Query, 0..99
    rows = [[f"Q{i}"] + ["" for _ in range(N_ITERS)]      # matriz vazia 22 x 101
            for i in range(1, N_QUERIES + 1)]
    row_idx = {f"Q{i}": i-1 for i in range(1, N_QUERIES + 1)}  # mapa nome->índice da linha

    for it in range(N_ITERS):                             # para cada iteração (coluna)
        resultados = executar_queries_concorrente(8)      # roda Q1..Q22 em paralelo (8 threads)
        for qname, dur_us in resultados:                  # preenche coluna 'it' com tempos
            rows[row_idx[qname]][it + 1] = str(dur_us)    # +1 por causa da coluna "Query"

    with open(CSV_PATH, "w", newline="") as f:            # escreve CSV final
        writer = csv.writer(f)
        writer.writerow(header)                           # cabeçalho
        writer.writerows(rows)                            # dados

if __name__ == "__main__":
    main()                                                # entrypoint

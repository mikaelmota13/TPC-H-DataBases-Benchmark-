import os, time, psycopg2, csv                           # módulos padrão, timer, driver Postgres e CSV
from concurrent.futures import ThreadPoolExecutor, as_completed  # pool de threads e iteração por conclusão

DB_CONFIG = {                                            # config de conexão ao Postgres
    "dbname": "tpch", "user": "postgres", "password": "postgres",
    "host": "localhost", "port": 5432
}
QUERIES_DIR = r"tpch-kit\dbgen\queries_resolved"         # pasta com q1.sql ... q22.sql
N_QUERIES = 22                                           # total de queries TPC-H
MAX_PAR = 10                                             # grau de paralelismo (até 10 queries simultâneas)
DURATION_SEC = 120                                       # duração-alvo por query (2 min)
CSV_PATH = "tpch_throughput_2min_distinct_queries.csv"   # arquivo de saída

def ajustar_sql(sql: str) -> str:
    return (sql.replace("day (3)", "day")                # corrige 'interval ... day (3)' -> Postgres
               .replace("limit -1", "")                  # remove 'limit -1' (sem sentido no PG)
               .replace(");\nlimit", "\nlimit")          # corrige LIMIT após ';'
               .replace(";\nlimit", "\nlimit")           # idem
               .strip())                                 # remove espaços/quebras nas bordas

def carregar_sql(i: int) -> str:
    path = os.path.join(QUERIES_DIR, f"q{i}.sql")        # monta caminho do arquivo da query
    with open(path, "r") as f:                           # abre o SQL
        return ajustar_sql(f.read())                     # lê e aplica ajustes de dialeto

def worker_query(i: int, duration_sec: int) -> int:
    sql = carregar_sql(i)                                # carrega SQL da query i
    stop_ts = time.perf_counter() + duration_sec         # timestamp de parada (agora + duração)
    conn = psycopg2.connect(**DB_CONFIG)                 # abre conexão dedicada da thread
    conn.autocommit = True                               # evita overhead de transação (apenas leitura)
    count = 0                                            # contador de execuções concluídas
    try:
        with conn.cursor() as cur:                       # cursor por conexão
            while time.perf_counter() < stop_ts:         # laço até atingir o tempo-alvo
                try:
                    cur.execute(sql)                     # executa a query
                    _ = cur.fetchall() if cur.description else None  # drena resultado (libera cursor)
                    count += 1                           # conta execução bem-sucedida
                except Exception:                        # falhas não contam
                    pass
    finally:
        conn.close()                                     # garante fechamento da conexão
    return count                                         # retorna total executado no período

def chunked(iterable, size):
    it = list(iterable)                                  # materializa para indexação
    for start in range(0, len(it), size):                # percorre em passos 'size'
        yield it[start:start+size]                       # retorna fatia (lote)

def main():
    totals = {f"Q{i}": 0 for i in range(1, N_QUERIES + 1)}   # dicionário de contagens por query

    # processa em lotes de até MAX_PAR queries simultâneas (cada thread roda 1 query fixa)
    for batch in chunked(range(1, N_QUERIES + 1), MAX_PAR):
        with ThreadPoolExecutor(max_workers=len(batch)) as ex:       # pool do tamanho do lote
            futs = {ex.submit(worker_query, i, DURATION_SEC): i for i in batch}  # dispara workers
            for fut in as_completed(futs):                            # coleta conforme terminam
                i = futs[fut]                                         # identifica qual query
                totals[f"Q{i}"] = fut.result()                        # salva a contagem
                print(f"Q{i}: {totals[f'Q{i}']} execuções em {DURATION_SEC}s")  # log

    # grava CSV com uma linha por query e a contagem em 120s
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Query", f"execucoes_{DURATION_SEC}s"])           # cabeçalho
        for i in range(1, N_QUERIES + 1):
            w.writerow([f"Q{i}", totals[f"Q{i}"]])                    # linha da Q_i

if __name__ == "__main__":
    main()                                                            # ponto de entrada

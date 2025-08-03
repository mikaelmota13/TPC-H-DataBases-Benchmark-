import psycopg2
import time
import os
import psutil

DB_CONFIG = {
    "dbname": "tpch",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}
QUERIES_DIR = r"tpch-kit\dbgen\queries_resolved"

def run_queries():
    results = []
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    psql_proc = [p for p in psutil.process_iter(['name']) if 'postgres' in p.info['name'].lower()]

    for i in range(1, 23):
        query_file = os.path.join(QUERIES_DIR, f"q{i}.sql")
        with open(query_file, 'r') as f:
            sql = f.read()

        print(f"Q{i}... ", end="")
        start = time.perf_counter()
        cpu_before = sum(p.cpu_percent(interval=None) for p in psql_proc)
        mem_before = sum(p.memory_info().rss for p in psql_proc)
        
        # isso aqui é pra ajustar pro postgres entender, pq ele n aceita o formato que ta na queria mas n sei se isso é certo fzr
        #quando a gente gera as queries pelo qgen, ele deixa a formatação de algumas cisas no formato que os postgres n aceita 
        sql = (
            sql.replace("day (3)", "day")
               .replace("limit -1", "")
               .replace(");\nlimit", "\nlimit")
               .replace(";\nlimit", "\nlimit")
               .strip()
        )
        
        cursor.execute(sql)
        _ = cursor.fetchall() if cursor.description else None

        cpu_after = sum(p.cpu_percent(interval=0.1) for p in psql_proc)
        mem_after = sum(p.memory_info().rss for p in psql_proc)
        end = time.perf_counter()

        duration = end - start
        cpu = cpu_after
        ram = (mem_after - mem_before) / (1024**2)  # em MB

        print(f"{duration:.2f}s | CPU: {cpu:.1f}% | RAM : {ram:.1f}MB")
        results.append((f"Q{i}", duration, cpu, ram))

    cursor.close()
    conn.close()

    return results

if __name__ == "__main__":
    data = run_queries()


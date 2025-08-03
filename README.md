# TPC-H Benchmark com PostgreSQL e Docker

Este projeto configura e executa o benchmark TPC-H usando:

- Geração de dados com `dbgen`
- Banco PostgreSQL via Docker
- Importação e execução das queries TPC-H
- Benchmark com medição de tempo
---

## Estrutura do Projeto

- `tpch-kit/`: Kit oficial TPC-H com geradores de dados e queries.
  - `dbgen/`: Contém `dbgen`, `qgen` e templates SQL.
  - `queries_resolved/`: Queries TPC-H geradas com valores concretos.
- `tpch-schema.sql`: Criação das tabelas no banco PostgreSQL.
- `run_tpch.py`: Executa todas as 22 queries, medindo tempo, CPU e RAM.
- `README.md`: Este arquivo com instruções completas.


---

## Execução

### Linux / WSL

```sh
sudo apt-get install git make gcc
git clone https://github.com/gregrahn/tpch-kit.git
cd tpch-kit/dbgen
make MACHINE=LINUX DATABASE=POSTGRESQL
```

### macOS

```sh
xcode-select --install
git clone https://github.com/gregrahn/tpch-kit.git
cd tpch-kit/dbgen
make MACHINE=MACOS DATABASE=POSTGRESQL
```

## Utilização

1. Gere os dados com o `dbgen`:
   ```sh
    cd tpch-kit/dbgen
    ./dbgen -s 1
   ```
2. Subir o PostgreSQL com Docker:
   ```sh
    docker run -d --name tpch-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres
    docker exec -it tpch-postgres psql -U postgres -c "CREATE DATABASE tpch;"
   ```
3. Criar o esquema TPC-H:
   ```sh
    docker cp tpch-schema.sql tpch-postgres:/tpch-schema.sql
    docker exec -it tpch-postgres psql -U postgres -d tpch -f /tpch-schema.sql
   ```
4. Carregar os dados `.tbl` no banco:
   ```sh
    for tbl in region nation part supplier partsupp customer orders lineitem; do
      docker cp tpch-kit/dbgen/${tbl}.tbl tpch-postgres:/${tbl}.tbl
      docker exec -it tpch-postgres psql -U postgres -d tpch -c "\COPY $tbl FROM '/$tbl.tbl' WITH DELIMITER '|' CSV"
    done
   ```
5. Gerar queries resolvidas com `qgen`:
   ```sh
    cd tpch-kit/dbgen
    cp ../dists.dss .
    cp ../queries/*.sql .
    mkdir -p queries_resolved
    for i in {1..22}; do ./qgen -d $i > queries_resolved/q${i}.sql; done
   ```
6. Depois você pode rodar com:
   ```sh
   python3 run_tpch.py
   ```
   ou pode executar as células separadamente no Jupyter Notebook em `main.ipynb`

## Referências

- [TPC-H Benchmark](http://www.tpc.org/tpch)

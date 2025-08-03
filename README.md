# TPC-H Benchmark com PostgreSQL e Docker

Benchmark TPC-H implementado:

- Geração de dados com `dbgen`
- Banco PostgreSQL via Docker
- Importação e execução das queries TPC-H
- Benchmark com medição de tempo
---

## Estrutura

- `tpch-kit/`: Kit oficial TPC-H com geradores de dados e queries.
  - `dbgen/`: Contém `dbgen`, `qgen` e templates SQL.
  - `queries_resolved/`: Queries TPC-H geradas com valores concretos.
- `tpch-schema.sql`: Criação das tabelas no banco PostgreSQL.
- `run_tpch.py`: Executa todas as 22 queries medindo o tempo.

## Componentes do TPC-H
<img width="615" height="693" alt="sample-data-tpch-schema" src="https://github.com/user-attachments/assets/95e30211-2f48-41c2-9ed8-d2a1745b0188" />

fonte: [TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf)

### O esquema TPC-H representa um modelo relacional com 8 tabelas:

* **PART (P\_)** -
  Descreve peças (parts):
  - Chave primária: `PARTKEY`
  - Colunas: `NAME`, `MFGR`, `BRAND`, `TYPE`, `SIZE`, `CONTAINER`, `RETAILPRICE`, `COMMENT`

* **SUPPLIER (S\_)** -
  Fornecedores de peças:
  - Chave primária: `SUPPKEY`
  - Colunas: `NAME`, `ADDRESS`, `NATIONKEY`, `PHONE`, `ACCTBAL`, `COMMENT`

* **PARTSUPP (PS\_)** -
  Tabela de relação N\:N entre PART e SUPPLIER:
  - Chave composta: (`PARTKEY`, `SUPPKEY`)
  - Colunas: `AVAILQTY`, `SUPPLYCOST`, `COMMENT`

* **CUSTOMER (C\_)** -
  Clientes:
  - Chave primária: `CUSTKEY`
  - Colunas: `NAME`, `ADDRESS`, `NATIONKEY`, `PHONE`, `ACCTBAL`, `MKTSEGMENT`, `COMMENT`

* **ORDERS (O\_)** - 
  Pedidos de clientes:
  - Chave primária: `ORDERKEY`
  - Chave estrangeira: `CUSTKEY` → CUSTOMER
  - Colunas: `ORDERSTATUS`, `TOTALPRICE`, `ORDERDATE`, `ORDERPRIORITY`, `CLERK`, `SHIPPRIORITY`, `COMMENT`

* **LINEITEM (L\_)** -
  Itens de cada pedido:
  - Chave composta: (`ORDERKEY`, `LINENUMBER`)
  - Chaves estrangeiras: `ORDERKEY` → ORDERS, `PARTKEY` → PART, `SUPPKEY` → SUPPLIER
  - Colunas: `QUANTITY`, `EXTENDEDPRICE`, `DISCOUNT`, `TAX`, `RETURNFLAG`, `LINESTATUS`, `SHIPDATE`, `COMMITDATE`, `RECEIPTDATE`, `SHIPINSTRUCT`, `SHIPMODE`, `COMMENT`

* **NATION (N\_)** -
  Países:
  - Chave primária: `NATIONKEY`
  - Chave estrangeira: `REGIONKEY` → REGION
  - Colunas: `NAME`, `COMMENT`

* **REGION (R\_)** -
  Regiões:
  - Chave primária: `REGIONKEY`
  - Colunas: `NAME`, `COMMENT`

### Relacionamentos:

* 1\:N de:

  * REGION → NATION
  * NATION → CUSTOMER e SUPPLIER
  * CUSTOMER → ORDERS
  * ORDERS → LINEITEM
  * PART e SUPPLIER → PARTSUPP
  * PARTSUPP → LINEITEM

### Obs:

  * As setas indicam o lado "muitos" das relações 1\:N.
  * O sufixo `SF` indica o scale factor, i.e., cardinalidade aproximada com base no tamanho da base.
    Ex.: `LINEITEM` ≈ SF \* 6.000.000.
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



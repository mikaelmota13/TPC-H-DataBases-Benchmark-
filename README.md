# TPC-H Benchmark Project

Este projeto contém o kit TPC-H para geração de dados e queries de benchmark, além de scripts auxiliares para facilitar o uso.

## Estrutura do Projeto

- `tpch-kit/`: Kit oficial TPC-H com modificações.
  - `dbgen/`: Ferramenta para geração dos dados de benchmark.
  - `ref_data/`: Dados de referência para testes e validação.
  - `README.md`: Documentação do kit TPC-H.
- `tpch-schema.sql`: Script SQL para criação do esquema do banco de dados TPC-H.
- `generate_queries.sh`: Script para geração dos queries do benchmark.
- `load_tpch.sh`: Script para carregar os dados gerados no banco de dados.
- `main.ipynb`: Notebook para análise ou manipulação dos dados.
- `note.txt`: Notas e observações do projeto.

## Instalação

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
   ./dbgen -s <ESCALA>
   ```
2. Crie o esquema do banco usando `tpch-schema.sql`.
3. Carregue os dados usando `load_tpch.sh`.
4. Gere queries com `generate_queries.sh`.

## Referências

- [TPC-H Benchmark](http://www.tpc.org/tpch)
- Documentação oficial no arquivo [`tpch-kit/README.md`](tpch-kit/README.md)

## Licença

Consulte o arquivo [`tpch-kit/EULA.txt`](tpch-kit/EULA.txt) para
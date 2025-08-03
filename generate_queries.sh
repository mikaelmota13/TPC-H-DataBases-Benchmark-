#!/bin/bash

# Caminho base
BASE_DIR=./tpch-kit/dbgen
cd "$BASE_DIR" || exit 1

# Verifica se qgen existe
if [ ! -f qgen ]; then
    echo "qgen não encontrado. Compile primeiro com: make MACHINE=LINUX DATABASE=POSTGRESQL"
    exit 1
fi

# Cria diretório de saída se não existir
OUT_DIR=./queries
mkdir -p "$OUT_DIR"

# Gera queries Q1 a Q22 com parâmetros resolvidos
for i in {1..22}; do
    ./qgen -d -s 1 $i > "$OUT_DIR/q${i}.sql"
    echo "Gerada: q${i}.sql"
done

echo "Queries geradas em $BASE_DIR/queries/"

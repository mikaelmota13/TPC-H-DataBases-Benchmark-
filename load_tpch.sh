#!/bin/bash

# Parâmetros
CONTAINER=tpch-postgres
DB=tpch
USER=postgres
PASS=postgres
PORT=5432
SCHEMA=tpch-schema.sql
DATA_DIR=./tpch-kit/dbgen

# 1. Subir PostgreSQL
docker run -d --name $CONTAINER -e POSTGRES_PASSWORD=$PASS -p $PORT:5432 postgres

# Espera iniciar
echo "Aguardando inicialização do PostgreSQL..."
sleep 10

# 2. Criar banco
docker exec -i $CONTAINER psql -U $USER -c "CREATE DATABASE $DB;"

# 3. Copiar esquema
docker cp $SCHEMA $CONTAINER:/$SCHEMA

# 4. Executar esquema
docker exec -i $CONTAINER psql -U $USER -d $DB -f /$SCHEMA

# 5. Copiar arquivos .tbl e importar
for tbl in region nation part supplier partsupp customer orders lineitem; do
  FILE="$DATA_DIR/$tbl.tbl"
  docker cp "$FILE" "$CONTAINER":/"$tbl.tbl"
  docker exec -i $CONTAINER psql -U $USER -d $DB -c "\COPY $tbl FROM '/$tbl.tbl' WITH DELIMITER '|' CSV"
done

echo "Importação concluída."

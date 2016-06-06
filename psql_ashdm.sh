PGPASSWORD=mysecretpassword
docker run -it --rm --link ashdb-postgres:postgres -e PGPASSWORD=$PGPASSWORD postgres psql -h postgres -U postgres

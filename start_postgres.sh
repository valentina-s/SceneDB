# get the postgres image
docker pull postgres

# start server
PGPASSWORD=mysecretpassword
docker run --name ashdb-postgres -e POSTGRES_PASSWORD=$PGPASSWORD -p 5432:5432 -d postgres

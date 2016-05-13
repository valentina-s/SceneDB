

I am trying to get python container to work (see Dockerfile) (but need to retry with proper internet conncetion)


Easier alternative is just to expose postgres server container's port 5432 to the host (docker-machine is host on OSX)

docker run --name some-postgres-2 -e POSTGRES_PASSWORD=$PGPASSWORD -p 5432:5432 -d postgres

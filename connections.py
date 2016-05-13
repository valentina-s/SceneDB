import boto3
import os
import psycopg2
import subprocess


s3 = boto3.client('s3')

if os.uname()[0] == 'Darwin':
    # docker runs within docker-machine on OSX
    host = subprocess.check_output('docker-machine ip default', shell=True).strip()
else:
    host = 'localhost'

port = 5432

_pgpassword = 'mysecretpassword'
db = psycopg2.connect("dbname=postgres user=postgres host={pghost} port={pgport} password={pgpassword}".format(
    pghost=host, pgport=port, pgpassword=_pgpassword))

# initial setup
#-----------------------------------------------

sudo apt-get install ffmpeg
sudo apt-get install pip
sudo apt-get update
sudo apt-get install python-pip
pip install –upgrade pip
sudo apt-get install virtualenv

# setup virtualenv (why not conda)
sudo apt-get install python-psycopg2


sudo apt-get install libssl-dev
pip install gcs_oauth2 boto plugin

sudo apt-get install docker-engine

# I might not need that
# sudo vim /etc/apt/sources.list.d/docker.list
# sudo apt-get update
# sudo apt-get purge lxc-docker
# apt-cache policy docker-engine

# pip install boto3

# run
# ----------------------------------------------
# sudo service docker start

# sudo docker ps -a
# ./ashdm_psql.sh

# initial setup
#-----------------------------------------------

sudo apt-get install -y ffmpeg
sudo apt-get install -y pip
sudo apt-get -y update
sudo apt-get install -y python-pip
sudo pip install –upgrade pip
sudo apt-get install -y virtualenv

# setup virtualenv (why not conda)
sudo apt-get install -y python-psycopg2


sudo apt-get install -y libssl-dev
sudo pip install gcs-oauth2-boto-plugin


sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-engine

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

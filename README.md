# SceneDB

Database for OOI CamHD, where video files are indexed by scenes

## Setup and run the database

1. Launch and ssh into a google compute engine instance.
2. Install requirements on the instance:

libraries/tools:

- ffmpeg
- docker (for running postgresql)

python modules

- boto
- gcs_oauth2_boto_plugin
- psycopg2

You can also run the setup script (for Ubuntu 16.04)
```{bash}
  bash instance_setup.sh
```


3. Create the postgresql database

```{bash}
# start the postgresql server
./start_postgres.sh

# create the ashdm database tables
python create_db.py
```

This will create two tables: `scenes` and `scene_bounds`.

## Inserting videos

These instructions assume the videos are already in a Google Storage bucket called `escience_camhd`.

To be able to read/write to Google Storage buckets, be sure you are authenticated.
If you are using the [default service account](https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances) and that service account has permission to access your bucket, then your instance terminal session will be authenticated already.

### Populate the `scene_bounds` for a set of videos

The following command processes\* all the videos to find their scene bounds.

```bash
python index_videos.py \
   --src-uri gs://escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04 \
   --find-scene-bounds
```

\* Right now the *processing* is a stub that inserts hardcoded bounds for each video.

### Index the set of videos


The following command will take all the mp4 files in `gs://escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04` and index them into the scenes specified in the `scene_bounds` table.

```bash
python index_videos.py \
   --src-uri gs://escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04 \
   --dst-uri gs://bdmyers_escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04/scenes
```

The overall result is new rows in the `scenes` table and new video files in `gs://bdmyers_escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04/scenes`.


## Querying the database

For now you can think of a query as being specified by two things: a SQL query that returns URLs of scenes and code that does something with each scene file.
See an example query of the ashdm database in `example_query.py`.

## Looking at the underlying tables directly

Run the postgresql shell with `./ashdm_psql.sh`

# ashdm

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

3. Create the postgresql database

```bash
# start the postgresql server
./start_postgres.sh

# create the ashdm database tables
python create_db.py
```

This will create two tables: `scenes` and `scene_bounds`.

## Index some videos

These instructions assume the videos are already in a Google Storage bucket called `escience_camhd`.

The following command will take all the mp4 files in `gs://escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04` and index them into the scenes specified in the `scene_bounds` table.

```bash
python index_videos.py \
   --src-uri gs://escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04 \
   --dst-uri gs://bdmyers_escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04/scenes
```

The overall result is new rows in the `scenes` table and new video files in `gs://bdmyers_escience_camhd/files/RS03ASHS/PN03B/06-CAMHDA301/2016/04/04/scenes`.


## Querying the database

See an example query of the ashdm database in `example_query.py`.

## Finding the scenes

Currently, the `scene_bounds` table is hardcoded in `create_db.py`. We've found that for reliable scene extraction, scenes must be found by processing each video individually.

In the near future, we will modify the schema of the `scene_bounds` table to include the video date (unique identifier of videos) as follows:

```sql
scene_bounds (scene_id integer, video_date timestamp, starts decimal, ends decimal, PRIMARY KEY(scene_id, video_date));
```

A scene-finding program should insert into this `scene_bounds` table.

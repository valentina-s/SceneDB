from connections import db


def create_db():
    cur = db.cursor()
    cur.execute("CREATE TABLE scene_bounds (scene_id integer, starts decimal, ends decimal, PRIMARY KEY(scene_id));")
    cur.execute("CREATE TABLE scenes (video_date timestamp, scene_id integer, url text, PRIMARY KEY(video_date, scene_id), FOREIGN KEY(scene_id) references scene_bounds(scene_id));")

    cur.execute("insert into scene_bounds values (0, 0.0, 5.5);")
    cur.execute("insert into scene_bounds values (1, 10.5, 15.5);")
    cur.execute("insert into scene_bounds values (2, 20.5, 25.5);")
    cur.execute("insert into scene_bounds values (3, 30.5, 35.5);")
    # TODO .. rest of scene ids

    db.commit()


if __name__ == '__main__':
    create_db()

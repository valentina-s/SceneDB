from connections import db


def create_db():
    cur = db.cursor()
    cur.execute("CREATE TABLE scene_bounds (scene_id integer, starts decimal, ends decimal, PRIMARY KEY(scene_id));")
    cur.execute("CREATE TABLE scenes (video_date timestamp, scene_id integer, url text, PRIMARY KEY(video_date, scene_id), FOREIGN KEY(scene_id) references scene_bounds(scene_id));")

    cur.execute("insert into scene_bounds values (%s, %s, %s)", (0, 42, 45))
    cur.execute("insert into scene_bounds values (%s, %s, %s)", (1, 1*60+3, 1*60+12))
    cur.execute("insert into scene_bounds values (%s, %s, %s)", (2, 1*60+28, 1*60+32))
    cur.execute("insert into scene_bounds values (%s, %s, %s)", (3, 1*60+38, 2*60+7))
    # TODO .. rest of scene ids

    db.commit()


if __name__ == '__main__':
    create_db()

from connections import db


def create_db():
    cur = db.cursor()

    cur.execute("""CREATE TABLE scene_bounds (
                                    scene_id integer,
                                    video_date timestamp,
                                    starts decimal,
                                    ends decimal,
                                    PRIMARY KEY(video_date, scene_id));
                                    """)

    cur.execute("""CREATE TABLE scenes (
                        video_date timestamp,
                        scene_id integer,
                        url text,
                        PRIMARY KEY(video_date, scene_id),
                        FOREIGN KEY(video_date, scene_id) references scene_bounds(video_date, scene_id));
                        """)

    db.commit()


if __name__ == '__main__':
    create_db()

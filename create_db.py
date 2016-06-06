from connections import db


def create_db():
    cur = db.cursor()

    cur.execute("""CREATE TABLE scene_bounds (
                                    video_date timestamp,
                                    scene_id integer,
                                    method text,
                                    starts decimal,
                                    ends decimal,
                                    PRIMARY KEY(video_date, scene_id, method));
                                    """)

    cur.execute("""CREATE TABLE scenes (
                        video_date timestamp,
                        scene_id integer,
                        method text,
                        url text,
                        PRIMARY KEY(video_date, scene_id, method),
                        FOREIGN KEY(video_date, scene_id, method) references scene_bounds(video_date, scene_id, method));
                        """)

    db.commit()


if __name__ == '__main__':
    create_db()

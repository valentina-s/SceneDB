import os
import re
from connections import s3, db
import glob

dir = '/Users/brandon/escience/video_analytics/docker-opencv/data/videos'


def video_files():
    # TODO download files
    for fn in glob.glob(os.path.join(dir, 'opendap_hyrax_large_format_*CAMHDA*CAMHDA*T*Z.mp4')):
        yield fn


class FileHandle(object):
    def __init__(self, name):
        self._name = name
        self._released = False

    def name(self):
        return self._name

    def release(self):
        assert not self._released, "Already released"

        self._released = True
        # TODO delete the temporary file

def scenes(filename):
    fullpath, ext = os.path.splitext(filename)
    base, keyb = os.path.split(fullpath)

    # TODO opencv split
    for i in [0,1,2,3]:
        key = "{keyb}_{scene}{ext}".format(keyb=keyb, scene=i, ext=ext)
        yield i, key, FileHandle(os.path.join(base, key))


timestamp_pat = re.compile(r'CAMHDA\d+-(?P<year>\d\d\d\d)(?P<month>\d\d)(?P<day>\d\d)T(?P<hour>\d\d)\d+Z')
def extract_timestamp(filename):
    m = timestamp_pat.search(filename)
    if not m:
        raise ValueError("could not extract date from video file name {}".format(filename))
    # FIXME: extract time properly
    return "{year}-{month}-{day} {hour}:00:00".format(**m.groupdict())

cur = db.cursor()

for fn in video_files():
    t = extract_timestamp(fn)

    for id, key, data in scenes(fn):
        cur.execute("insert into scenes values (timestamp '{t}', {id}, '{key}')".format(t=t, id=id, key=key))
        db.commit()

        if False:
            with open(data.name()) as f:
                print s3.put_object(ACL='private',
                                        Body=f,
                                        Bucket='escience.washington.edu.camhd',
                                        Key=key)

        data.release()

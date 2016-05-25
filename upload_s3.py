import os
import re
from connections import s3, db
import connections
import glob
import Pyro4
import sys
from urlparse import urlparse
import argparse
import errno
import psycopg2

dir = '/Users/brandon/escience/video_analytics/docker-opencv/data/videos'

cur = db.cursor()

opencv_client = None

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
    base, keyb = os.path.split(filename)   # /local/path, camhd.mp4

    # TODO opencv split

    cur.execute("select scene_id, starts, ends from scene_bounds")
    all_bounds = list(cur.fetchall())

    # have to convert to float
    all_bounds = [(i, float(s), float(e)) for i, s, e in all_bounds]
    print all_bounds

    scene_clips = opencv_client.extract_scenes(keyb, all_bounds)

    for row, key in zip(all_bounds, scene_clips):
        yield row[0], key, FileHandle(os.path.join(base, key))


timestamp_pat = re.compile(
    r'CAMHDA\d+-(?P<year>\d\d\d\d)(?P<month>\d\d)(?P<day>\d\d)T(?P<hour>\d\d)\d+Z')


def extract_timestamp(filename):
    m = timestamp_pat.search(filename)
    if not m:
        raise ValueError("could not extract date from video file name {}".format(filename))
    # FIXME: extract time properly
    return "{year}-{month}-{day} {hour}:00:00".format(**m.groupdict())

for fn in video_files():
    t = extract_timestamp(fn)

    for id, key, data in scenes(fn):
        if False:
            with open(data.name()) as f:
                print s3.put_object(ACL='private',
                                        Body=f,
                                        Bucket='escience.washington.edu.camhd',
                                        Key=key)

        data.release()

        cur.execute("insert into scenes values (timestamp '{t}', {id}, '{key}')".format(t=t, id=id, key=key))
        db.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download raw videos, cut into scenes, and upload")
    parser.add_argument('--src-uri', dest='src_uri', required=True)
    parser.add_argument('--opencv-uri', dest='opencv_uri')

    opt = parser.parse_args(sys.argv[1:])

    if opt.opencv_uri:
        print '{uri}@{host}:7771'.format(uri=opt.opencv_uri, host=connections.host)
        opencv_client = Pyro4.Proxy('{uri}@{host}:7771'.format(uri=opt.opencv_uri, host=connections.host))
    else:
        sys.stderr.write("WARNING: No Pyro4 provided; opencv operations will fail\n")

    src_uri = urlparse(opt.src_uri)

    if src_uri.scheme == 'gs':
        import boto
        import gcs_oauth2_boto_plugin
        dir_uri = boto.storage_uri(src_uri.hostname + src_uri.path, 'gs')

        for obj in dir_uri.get_bucket():
            file_uri = boto.storage_uri(os.path.join(src_uri.hostname, obj.name), 'gs')
            local_dir = os.path.split(obj.name)[0]
            try:
                os.makedirs(local_dir)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(local_dir):
                    pass
                else:
                    raise exc

            print "saving ", obj.name
            with open(obj.name, 'wb') as tempf:
                file_uri.get_key().get_file(tempf)
    else:
        raise NotImplementedError("unsupported scheme {}".format(src_uri.scheme))


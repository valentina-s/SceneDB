import os
import re
from connections import s3, db
import connections
import glob
import sys
from urlparse import urlparse
import argparse
import errno
import ffmpeg_extract
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

    if opencv_client is not None:
        scene_clips = opencv_client.extract_scenes(keyb, all_bounds)
    else:
        scene_clips = ffmpeg_extract.extract_scenes(filename, all_bounds)
        # just keep the filename, we have the base
        for i in range(len(scene_clips)):
            scene_clips[i] = os.path.split(scene_clips[i])[1]

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download raw videos, cut into scenes, and upload")
    parser.add_argument('--src-uri', dest='src_uri', required=True, description="A directory with videos to process")
    parser.add_argument('--dst-uri', dest='dst_uri', required=True, description="A directory to save scenes to")
    parser.add_argument('--opencv-uri', dest='opencv_uri')

    opt = parser.parse_args(sys.argv[1:])

    if opt.opencv_uri:
        import Pyro4
        print '{uri}@{host}:7771'.format(uri=opt.opencv_uri, host=connections.host)
        opencv_client = Pyro4.Proxy('{uri}@{host}:7771'.format(uri=opt.opencv_uri, host=connections.host))
    else:
        # use ffmpeg
        pass

    src_uri = urlparse(opt.src_uri)
    dst_uri = urlparse(opt.dst_uri)

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

            print "saving locally temporarily:", obj.name
            with open(obj.name, 'wb') as tempf:
                file_uri.get_key().get_file(tempf)

            # extract and save
            t = extract_timestamp(obj.name)

            for id, key, data in scenes(obj.name):
                print "  uploading ", data.name()
                with open(data.name()) as f:
                    if dst_uri.scheme == 'gs':
                        ofile_uri = boto.storage_uri(os.path.join(dst_uri.hostname + dst_uri.path, key), 'gs)')
                        ofile_uri.new_key().set_contents_from_file(f)
                    else:
                        raise NotImplementedError("unsupported scheme {}".format(src_uri.scheme))

                data.release()

                cur.execute("insert into scenes values (timestamp '{t}', {id}, '{key}')".format(t=t, id=id, key=key))
                db.commit()
    else:
        raise NotImplementedError("unsupported scheme {}".format(src_uri.scheme))


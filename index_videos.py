import os
import re
from connections import s3, db
import connections
import sys
from urlparse import urlparse
import argparse
import errno
import ffmpeg_extract


cur = db.cursor()

opencv_client = None


class FileHandle(object):
    def __init__(self, name):
        self._name = name
        self._released = False

    def name(self):
        return self._name

    def release(self):
        assert not self._released, "Already released"

        self._released = True
        os.remove(self._name)


def scenes(filename, method):
    base, keyb = os.path.split(filename)   # /local/path, camhd.mp4

    # TODO opencv split

    cur.execute("""select scene_id, starts, ends from scene_bounds
                    where video_date=timestamp %s and method=%s""", (extract_timestamp(keyb), method))
    all_bounds = list(cur.fetchall())

    cur.execute("""select scene_id, method, starts, ends from scene_bounds
                    where video_date=timestamp %s and method=%s""", (extract_timestamp(keyb), method))
    all_bounds_with_method = list(cur.fetchall())

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

    for row, key in zip(all_bounds_with_method, scene_clips):
        yield row[0], row[1], key, FileHandle(os.path.join(base, key))


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
    parser.add_argument('--src-uri', dest='src_uri', required=True, help="A directory with videos to process")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dst-uri', dest='dst_uri', help="A directory to save scenes to")
    group.add_argument('--find-scene-bounds', dest='find_scene_bounds', action="store_true", help="*Stub* for finding scene bounds")
    parser.add_argument('--opencv-uri', dest='opencv_uri')
    parser.add_argument('--method', dest='method', help='extraction method', default='hardcoded')
    parser.add_argument('--cache-input-videos', action='store_true', dest='cache_input_videos', help='Do not remove local copy')

    opt = parser.parse_args(sys.argv[1:])

    if opt.opencv_uri:
        import Pyro4
        print '{uri}@{host}:7771'.format(uri=opt.opencv_uri, host=connections.host)
        opencv_client = Pyro4.Proxy('{uri}@{host}:7771'.format(uri=opt.opencv_uri, host=connections.host))
    else:
        # use ffmpeg
        pass

    src_uri = urlparse(opt.src_uri)
    print(src_uri)
    print(src_uri.hostname)
    if src_uri.scheme == 'gs':
        import boto
        import gcs_oauth2_boto_plugin
        dir_uri = boto.storage_uri(src_uri.hostname + src_uri.path, 'gs')

        # for obj in dir_uri.get_bucket():
        listOfPaths = [obj.name for obj in dir_uri.get_bucket() if src_uri.path[1:] in obj.name]

        for obj in listOfPaths:
            file_uri = boto.storage_uri(os.path.join(src_uri.hostname, obj), 'gs')
            print(obj)
            t = extract_timestamp(obj)

            if opt.dst_uri is not None:
                dst_uri = urlparse(opt.dst_uri)
                local_dir = os.path.split(obj)[0]
                print(local_dir)
                try:
                    os.makedirs(local_dir)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(local_dir):
                        pass
                    else:
                        raise exc

                if not opt.cache_input_videos:
                    print "saving locally temporarily:", obj
                else:
                    print "saving locally (won't remove automatically):", obj

                
                with open(obj, 'wb') as tempf:
                    print(file_uri)
		    print(type(file_uri))
                    print(src_uri.hostname)
                    file_uri.get_key().get_file(tempf)

                # extract and save

                for id, method, key, data in scenes(obj, opt.method):
                    print "  uploading ", data.name()
                    print(os.path.join(dst_uri.hostname + dst_uri.path, key))
                    
		    with open(data.name()) as f:
                        if dst_uri.scheme == 'gs':
                            ofile_uri = boto.storage_uri(os.path.join(dst_uri.hostname + dst_uri.path, key), 'gs')
		            print(ofile_uri)                           
                            ofile_uri.new_key().set_contents_from_file(f)
                            fullkey = "{s}://{b}/{o}".format(
                                s=ofile_uri.scheme,
                                b=ofile_uri.bucket_name,
                                o=ofile_uri.object_name)
                        else:
                            raise NotImplementedError("unsupported scheme {}".format(src_uri.scheme))

                    # done with local copy of this scene file
                    data.release()

                    cur.execute("insert into scenes values (timestamp %s, %s, %s, %s)", (t, id, method, fullkey))
                    db.commit()

                # delete the local copy of original video
		if not opt.cache_input_videos:
                    os.remove(obj)
            else:
                # TODO: Inserting fake scene bounds right now, but we really want to find them
                # by processing each video
                assert opt.method == 'hardcoded', "Only support hardcoded right now"
                print(obj)
                print(t)

                cur.execute("insert into scene_bounds values (timestamp %s, %s, %s, %s, %s)", (t, 0, 'hardcoded', 42, 45))
                cur.execute("insert into scene_bounds values (timestamp %s, %s, %s, %s, %s)", (t, 1, 'hardcoded', 1*60+3, 1*60+12))
                cur.execute("insert into scene_bounds values (timestamp %s, %s, %s, %s, %s)", (t, 2, 'hardcoded', 1*60+28, 1*60+32))
                cur.execute("insert into scene_bounds values (timestamp %s, %s, %s, %s, %s)", (t, 3, 'hardcoded', 1*60+38, 2*60+7))
                db.commit()
    else:
        raise NotImplementedError("unsupported scheme {}".format(src_uri.scheme))

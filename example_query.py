from connections import db
from urlparse import urlparse
import sys
import errno
import os

class GetSceneInEachQuery(object):

    """
    scene: a scene id in the scene_bounds table
    on_uri: function(name, uri) called for each scene file
    """
    def __init__(self, scene, on_uri):
        self._query = """select url from scenes S, scene_bounds SB
                        where S.scene_id = {}""".format(scene)
        self._on_uri = on_uri

    def execute(self):
        cur = db.cursor()
        cur.execute(self._query)

        results = cur.fetchall()

        if len(results) == 0:
            sys.stderr.write("WARNING: no scenes found for id\n")

        for row in results:
            url = urlparse(row[0])

            if url.scheme == 'gs':
                import boto
                import gcs_oauth2_boto_plugin
                file_uri = boto.storage_uri(url.hostname + url.path, 'gs')

                self._on_uri(url.path, file_uri)


if __name__ == '__main__':
    def save_file(name, uri):
        dirpath = os.curdir + os.path.dirname(name)+'/queryresult'
        try:
            os.makedirs(dirpath)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(dirpath):
                pass
            else:
                raise exc

        fn = os.path.join(dirpath, os.path.basename(name))

        with open(fn, 'wb') as f:
            uri.get_key().get_file(f)

    GetSceneInEachQuery(1, save_file).execute()


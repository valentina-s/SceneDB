import subprocess
import os


def extract_scenes(name, bounds):
    """
    :param name: input filename
    :param bounds: list of tuples (scene_id, start(sec), end(sec)
    :return: output filenames
    """

    files = []
    for (id, start, end) in bounds:
        basename, _ = os.path.splitext(name)
        outname = "{basename}_{scene}.mp4".format(basename=basename, scene=id)

        # TODO: might experiment with -ss args before and after -i
        subprocess.check_call("ffmpeg \
                                -y \
                              -ss {start} \
                              -i in.mp4 \
                              -to {duration} \
                              -c copy \
                              {outf}".format(
            start=start, duration=end-start, outf=outname),
                              shell=True)

        files.append(outname)

    return files

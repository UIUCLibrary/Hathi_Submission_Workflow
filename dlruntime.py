import urllib.request
import hashlib

import shutil
from collections import namedtuple
import os

Runtime = namedtuple("Runtime", ("url", "md5"))
#
# URL = "https://www.python.org/ftp/python/3.6.2/python-3.6.2-embed-amd64.zip"
# MD5 = "0fdfe9f79e0991815d6fc1712871c17f"

DESTINATION = "build/runtimes/"

RUNTIMES = {("3.6.2", "amd64"): Runtime("https://www.python.org/ftp/python/3.6.2/python-3.6.2-embed-amd64.zip",
                                        "0fdfe9f79e0991815d6fc1712871c17f")}


def valid_file(file, expected_md5):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_md5.update(chunk)
    if hash_md5.hexdigest() != expected_md5:
        raise IOError("{} doesn't match expected hash.")


def download_runtime(url, md5, destination):
    filename = os.path.basename(url)
    try:
        tmp_file, headers = urllib.request.urlretrieve(url)
        valid_file(tmp_file, md5)
        final_path = os.path.join(destination, filename)
        shutil.move(tmp_file, final_path)
        return os.path.abspath(final_path)

    finally:
        urllib.request.urlcleanup()


if __name__ == '__main__':
    print("Downloading runtime")
    runtime = RUNTIMES[("3.6.2", "amd64")]
    file_name = download_runtime(url=runtime.url, md5=runtime[1], destination=DESTINATION)
    print("Downloaded {}".format(file_name))
    # download_runtime(URL, MD5, DESTINATION)

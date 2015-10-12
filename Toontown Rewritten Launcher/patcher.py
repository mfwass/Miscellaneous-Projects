# Filename: patcher.py
# Created by: Michael Wass (11Oct2015)
#
# This scripts purpose is to update a players Toontown Rewritten installation
# and nothing more. This is fan-made, TTR cannot be held liable for any issues
# with this files usage. This script was tested on mac only.
#
# Enjoy - <3 mfwass.

import os
import sys
import bz2
import stat
import wget
import json
import time
import urllib2
import hashlib

class Patcher:
    def __init__(self):
        # declare the patch manifest location, we'll come back to you later <3
        manifest_url = 'http://s3.amazonaws.com/cdn.toontownrewritten.com/content/patchmanifest.txt'

        # the print says it all
        print "Gathering available mirrors..."

        self.mirrors = urllib2.urlopen('https://www.toontownrewritten.com/api/mirrors', timeout=30)
        self.mirrorList = json.loads(self.mirrors.read())

        if not self.mirrorList:
            # oh no! the main system has failed us, pesky little ----! oh well, let's use the backup...
            print "WARNING: Main system failed! Rolling over to backup mirror location..."
            self.mirrors = urllib2.urlopen('http://s3.amazonaws.com/cdn.toontownrewritten.com/mirrors.txt', timeout=30)
            self.mirrorList = json.loads(self.mirrors.read())

        # Tell how many mirrors we have
        print "Obtained %s mirrors." % len(self.mirrorList)

        # we've come back for you patchmanifest.txt
        manifest = urllib2.urlopen(manifest_url).read()
        self.manifest = json.loads(manifest)

        del manifest # cleanup

        # okay, we have our patching info. now to actually patch the stuff
        print "Checking for updates..."
        self.patch()

    def patch(self):
        # begin downloading files...
        counter = 0
        skipped = 0
        updated = 0

        for file in self.manifest:
            counter += 1

            print '\r', "Updating file '%s' (%s / %s)..." % (file, counter, len(self.manifest)),
            sys.stdout.flush()

            # Find the rest of the data
            item = self.manifest.get(file)

            # Check to see if the files are required on our platform.
            if sys.platform not in item.get('only', ['linux2', 'win32', 'darwin']):
                # Not on our platform, IGNORE!
                print "Skipped file %s. Not required on this platform.\n" % file,

                skipped += 1
                continue

            # call another class to handle the downloading of it.
            fileupdate = PatchFile(file, fileHash=item.get('hash'), compressedHash=item.get('compHash'), downloadName=item.get('dl'), mirrors=self.mirrorList)

        print "Done updating files.\nChecked %s | Skipped %s" % (counter, skipped)

class PatchFile:
    def __init__(self, filename, fileHash=None, compressedHash=None, downloadName=None, mirrors=None):
        # Declare variables.
        self.filename = filename
        self.fileHash = fileHash
        self.compHash = compressedHash
        self.downloadName = downloadName
        self.downloadPath = os.getcwd()
        self.downloadedFilePath = self.downloadPath + "/" + self.downloadName
        self.filePath = os.path.join(self.downloadPath, filename)
        self.mirrors = mirrors

        # actually patch the files
        self.patch()

    def patch(self):
        if not os.path.exists(self.filePath):
            # File did not exist, download it.
            self.download()
        else:
            if self.fileHash == self.getDownRegFileHash():
                # files up to date, goooood gooood (darth sidious face)
                print "Up to date."
                return
            # Okay, files are out of date. TODO patches -- for now, download full file:
            self.download()


    def getDownRegFileHash(self):
        # grabs file hash -- taken from
        # http://pythoncentral.io/hashing-files-with-python/
        BLOCKSIZE = 65536
        hasher = hashlib.sha1()

        with open(self.filename, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)

            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)

        return hasher.hexdigest()

    def download(self):
        for mirror in self.mirrors:
            try:
                # try using one of the mirrors
                self.patchFile(mirror)
                break
            except:
                # bad mirror, remove the mirror and let it try again.
                self.mirrors.remove(mirror)

    def patchFile(self, url):
        # This is needed to keep the output pretty.
        print "\n"

        downloadUrl = url + self.downloadName
        # libraries.bundle stuff (NOT DONE YET! TODO!)
        if '/' in self.downloadName:
            self.splitDownloadName = self.downloadName.split('/')

        # download the file
        file_name = wget.download(downloadUrl)

        # wait a second, let the file finish if it needs to.
        time.sleep(1)

        # open the file
        zipfile = bz2.BZ2File(self.downloadName)

        # get the decompressed data
        data = zipfile.read()

        # write a uncompressed file
        open(self.filename, 'wb').write(data)

        # only on mac, :)
        if sys.platform == "darwin":
            # change permissions, prevents "permission denied" bs
            os.chmod(self.filename, stat.S_IRWXU)

        # delete the compressed file
        os.unlink(self.downloadedFilePath)

        # we done, return.
        return

# debug
#if __name__ == "__main__":
#    Patcher()

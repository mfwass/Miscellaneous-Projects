# Filename: TTRLauncher.py
# Created by: Michael Wass (10Aug2015)
#
# This scripts purpose is to launch Toontown Rewritten and nothing more
# This launcher is fan-made, TTR cannot be held liable for any issues
# with its usage. This script was tested on mac only.
# 
# TODO: Check default TTR installation path.
#
# Enjoy - <3 mfwass.

import httplib
import urllib
import json
import os
import time
import subprocess
import getpass
import sys

class BasicLauncher():
    def __init__(self):
        # Get credentials
        username = raw_input('Username: ')
        # Use getpass instead of raw_input to hide inputted text.
        password = getpass.getpass()
        # Post credentials
        connectionInfo = self.postStuff(username=username, password=password)

    def postStuff(self, username=None, password=None):
        # Sanity checking
        if username and password:
            params = urllib.urlencode({'username': username, 'password': password})
        else:
            # Gotta provide a username/password
            print "ERROR: Please provide a username or password."
            sys.exit(1)
        self.connection = httplib.HTTPSConnection('www.toontownrewritten.com', 443)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        self.connection.request('POST', '/api/login?format=json', params, headers)
        response = self.connection.getresponse()
        jsonresponse = json.loads(response.read())
        success = jsonresponse.get('success', 'false')
        if success == 'true':
            gameserver = jsonresponse.get('gameserver', None)
            cookie = jsonresponse.get('cookie', None)
            print "Successful response.\nCookie = %s\nGame Server = %s\n" % (cookie, gameserver)
            self.launchGame(gameserver=gameserver, cookie=cookie)
        elif success == 'delayed':
            # They're delayed, so lets use their queue token
            queueToken = jsonresponse.get('queueToken', None)
            eta = jsonresponse.get('eta', None)
            position = jsonresponse.get('position', None)
            print "Delayed response.\nQueue token = %s\nETA = %s\nPosition = %s\n" % (queueToken, eta, position)
            params = urllib.urlencode({'queueToken': queueToken})
            # ugly, todo make pretty.
            while success == 'delayed':
                # So we aren't spamming the login server, request every two seconds.
                time.sleep(2)
                self.connection = httplib.HTTPSConnection('www.toontownrewritten.com', 443)
                headers = {'Content-type': 'application/x-www-form-urlencoded'}
                self.connection.request('POST', '/api/login?format=json', params, headers)
                # read response.
                response = self.connection.getresponse()
                jsonresponse = json.loads(response.read())
                success = jsonresponse.get('success', 'false')
                if success == 'true':
                    print "Server responded, successful login. Launching game...\n\n"
                    # woohoo, we're in! Let's grab those env variables 
                    # and get this party started.
                    gameserver = jsonresponse.get('gameserver', None)
                    cookie = jsonresponse.get('cookie', None)
                    # launch game.
                    self.launchGame(gameserver=gameserver, cookie=cookie)
                else:
                    # Just incase the server changes its mind.
                    print "Something went wrong, please try again."
                    sys.exit(0)
        elif success == 'partial':
            raise NotImplementedError("Two-step login is not implemented at this time")
        elif success == 'false':
            banner = jsonresponse.get('banner', None)
            print banner
            sys.exit(0)
        else:
            print "Unknown error. This may be caused by a new message type being added and not implemented into the launcher."
            print "JSON response: %s" % jsonresponse

    def launchGame(self, gameserver=None, cookie=None):
        # Get current script location
        currPath = os.getcwd()
        # Add a / to the path.
        path = currPath + "/"
        # Set env variables
        os.environ['TTR_PLAYCOOKIE'] = cookie
        os.environ['TTR_GAMESERVER'] = gameserver
        # Open the game.
        if sys.platform == 'win32':
            # Check if files are installed
            try:
                game = subprocess.Popen('./TTREngine')
            except:
                print "ERROR: This script will only launch the game using previously installed files. Please install TTR and try again.\nIf TTR is already installed, please put this script in the location of your currently installed files.\nThis script is located at %s" % path
                sys.exit(1)
        elif sys.platform == 'darwin':
            # Check if game files are installed
            try:
                # Getting this to open successfully made me hate python with a bloody passion
                game = os.system("export DYLD_LIBRARY_PATH='%s'Libraries.bundle\n'%s'./Toontown\ Rewritten" % (path, path))
            except:
                print "ERROR: This script will only launch the game using previously installed files. Please install TTR and try again.\nIf TTR is already installed, please put this script in the location of your currently installed files.\nThis script is located at %s" % path
                sys.exit(1)
        elif sys.platform == 'linux':
            try:
                game = subprocess.Popen('./TTREngine')
            except:
                print "ERROR: This script will only launch the game using previously installed files. Please install TTR and try again."
                sys.exit(1)
        if game != 0:
            # rip crash
            print "\n\nOh no! You crashed! Play again?"
            return
        print "\n\nPlay again? :D"
        return

BasicLauncher()
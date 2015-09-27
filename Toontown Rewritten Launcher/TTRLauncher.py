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

        # Begin checking response type
        if success == 'true':
            # Successful login
            # Get gameserver and token from response.
            gameserver = jsonresponse.get('gameserver', None)
            cookie = jsonresponse.get('cookie', None)
            
            # A print showing cookie and gameserver
            print "Successful response.\nCookie = %s\nGame Server = %s\n" % (cookie, gameserver)

            # Continue onward to launch game
            self.launchGame(gameserver=gameserver, cookie=cookie)

        elif success == 'delayed':
            # They're delayed, so lets grab their queue token, eta and position.
            queueToken = jsonresponse.get('queueToken', None)
            eta = jsonresponse.get('eta', None)
            position = jsonresponse.get('position', None)

            # Print to tell the user they're in the queue.
            print "Delayed response.\nQueue token = %s\nETA = %s\nPosition = %s\n" % (queueToken, eta, position)

            # Set up params for contacting the server again.
            params = urllib.urlencode({'queueToken': queueToken})

            # ugly, todo make pretty.
            while success == 'delayed':
                # So we aren't spamming the login server, request every two seconds.
                time.sleep(2)
                # Establish connection
                self.connection = httplib.HTTPSConnection('www.toontownrewritten.com', 443)
                headers = {'Content-type': 'application/x-www-form-urlencoded'}

                # Post our queue token
                self.connection.request('POST', '/api/login?format=json', params, headers)

                # Read response.
                response = self.connection.getresponse()
                jsonresponse = json.loads(response.read())

                # Check whether successful or not.
                success = jsonresponse.get('success', 'false')
                if success == 'true':
                    print "Server responded, successful login. Launching game...\n\n"
                    # Woohoo, we're in! Let's grab those env variables 
                    # and get this party started.
                    gameserver = jsonresponse.get('gameserver', None)
                    cookie = jsonresponse.get('cookie', None)

                    # Launch game.
                    self.launchGame(gameserver=gameserver, cookie=cookie)
                else:
                    # Just incase the server changes its mind.
                    print "Something went wrong, please try again."
                    sys.exit(0)

        elif success == 'partial':
            # Two step login/ToonGuard token.
            raise NotImplementedError("Two-step login is not implemented at this time")

        elif success == 'false':
            # No success, grab the reason why and print.
            banner = jsonresponse.get('banner', None)
            print banner
            sys.exit(0)
        else:
            # Unknown error, print out the raw response.
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
        # Windows
        if sys.platform == 'win32':
            # Check if files are installed
            try:
                game = subprocess.Popen('./TTREngine')
            except:
                # Files not installed
                print "ERROR: This script will only launch the game using previously installed files. Please install TTR and try again.\nIf TTR is already installed, please put this script in the location of your currently installed files.\nThis script is located at %s" % path
                sys.exit(1)

        # Mac (<3)
        elif sys.platform == 'darwin':
            # Check if game files are installed
            try:
                # Getting this to open successfully made me hate python with a bloody passion
                game = os.system("export DYLD_LIBRARY_PATH='%s'Libraries.bundle\n'%s'./Toontown\ Rewritten" % (path, path))
            except:
                # Files not installed
                print "ERROR: This script will only launch the game using previously installed files. Please install TTR and try again.\nIf TTR is already installed, please put this script in the location of your currently installed files.\nThis script is located at %s" % path
                sys.exit(1)

        # Linux
        elif sys.platform == 'linux':
            # Check if game files are installed
            try:
                game = subprocess.Popen('./TTREngine')
            except:
                # Files not installed
                print "ERROR: This script will only launch the game using previously installed files. Please install TTR and try again."
                sys.exit(1)

        if game != 0:
            # rip crash
            print "\n\nOh no! You crashed! Play again?"
            return
        # No other issues, ask if they want to play again. :)
        print "\n\nPlay again? :D"
        return

# Call the main class
BasicLauncher()

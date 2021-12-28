import os
import time
import threading
import subprocess
import ast
from unittest.mock import Mock

from syncplay import constants
from syncplay.players.iina import IinaPlayer
from syncplay.players.webtorrent_iina_ipc import WEBTORRENT_IINA
from syncplay.utils import isMacOS, isURL, findResourcePath, findWorkingDir
from syncplay.messages import getMessage

class WebtorrentIinaPlayer(IinaPlayer):
    @staticmethod
    def run(client, playerPath, filePath, args):
        '''Fork: renames IinaPlayer -> WebtorrentIinaPlayer.
        Important because this calls __init__
        Changes "player" path to webtorrent
        '''
        constants.MPV_NEW_VERSION = True
        constants.MPV_OSC_VISIBILITY_CHANGE_VERSION = True
        # "player" path is actually webtorrent (which uses mpv)
        if isMacOS():
            node_path = os.path.join(findWorkingDir(), 'node', 'bin', 'node')
            webtorrent_path = os.path.join(findWorkingDir(), 'webtorrent-cli', 'bin', 'cmd.js')
            playerPath = f'{node_path} {webtorrent_path}'
        else:
            playerPath = client._config['webtorrentPath']

        return WebtorrentIinaPlayer(client, playerPath, filePath, args)

    def _loadFile(self, filePath):
        '''Fork: replaced loadfile ipc call with launching the webtorrent process and then
        other stuff that only works when mpv is launched
        '''
        self._clearFileLoaded()
        # TODO load another magnet and see if the stuff below are still needed
        # from _preparePlayer
        #for key, value in constants.IINA_PROPERTIES.items():
        #    self._setProperty(key, value)
        #self._listener.sendLine(["load-script", findResourcePath("syncplayintf.lua")])
        ## end from _preparePlayer
        ## TLDR: this fixes a bug where IINA launches but Syncplay shows "no file opened"
        ## This is a hack for IINA -- when it opens the video it does not
        ## print the SyncplayUpdateFile, because (mpv-)term-playing-msg does not work
        ## on the command line (like Popen). Only upstream syncplay's method works,
        ## setting the property via sendLine in _preparePlayer. However, this cannot
        ## be done here as it requires IINA to be already running. Webtorrent does not
        ## launch IINA until receiving a magnet. The relevant 3 lines in _preparePlayer
        ## are in fact just above this section, but are in fact useless because
        ## term-playing-msg only fires when IINA opens a new file, not when a file
        ## is already opened
        ## This manually updates the current user's file to the magnet link
        ## This is inferior to mpv -- mpv is able to send the video length and
        ## proper path (not magnet)
        #self._client.currentUser.file = {
        #    'name': filePath,
        #    'duration': '???',
        #    'size': '???',
        #    'path': filePath
        #}
        ## Forcibly update the user list with the above information
        #self._client.showUserList()
        #self._client.initPlayer(self)

    def openFile(self, filePath, resetPosition=False):
        '''Fork: add debug message because it takes time to load and buffer'''
        self._client.ui.showDebugMessage(f'Loading and buffering magnet link {filePath}')
        self._client.ui.showDebugMessage("openFile, resetPosition=={}".format(resetPosition))
        if resetPosition:
            self.lastResetTime = time.time()
            if isURL(filePath):
                self._client.ui.showDebugMessage("Setting additional lastResetTime due to stream")
                self.lastResetTime += constants.STREAM_ADDITIONAL_IGNORE_TIME
        self._loadFile(filePath)
        if self._paused != self._client.getGlobalPaused():
            self._client.ui.showDebugMessage("Want to set paused to {}".format(self._client.getGlobalPaused()))
        else:
            self._client.ui.showDebugMessage("Don't want to set paused to {}".format(self._client.getGlobalPaused()))
        if resetPosition == False:
            self._client.ui.showDebugMessage("OpenFile setting position to global position: {}".format(self._client.getGlobalPosition()))
            self.setPosition(self._client.getGlobalPosition())
        else:
            self._storePosition(0)
        # TO TRY: self._listener.setReadyToSend(False)

    def __init__(self, client, playerPath, filePath, args):
        '''Fork: use modified WEBTORRENT_IINA ipc instead'''
        from twisted.internet import reactor
        self.reactor = reactor
        self._client = client
        self._set_defaults()

        self._playerIPCHandler = WEBTORRENT_IINA
        self._create_listener(playerPath, filePath, args)

    def _create_listener(self, playerPath, filePath, args):
        '''Fork: literally the same, only here to redirect __Listener to
        the one in this file rather than mpv.py
        '''
        try:
            self._listener = self.__Listener(self, self._playerIPCHandler, playerPath, filePath, args)
        except ValueError:
            self._client.ui.showMessage(getMessage("mplayer-file-required-notification"))
            self._client.ui.showMessage(getMessage("mplayer-file-required-notification/example"))
            self.drop()
            return
        except AttributeError as e:
            self._client.ui.showErrorMessage("Could not load mpv: " + str(e))
            return
        self._listener.setDaemon(True)
        self._listener.start()

        self._durationAsk = threading.Event()
        self._filenameAsk = threading.Event()
        self._pathAsk = threading.Event()

        self._positionAsk = threading.Event()
        self._pausedAsk = threading.Event()
        self._preparePlayer()

    class __Listener(threading.Thread):
        '''Fork: exact copy of __Listener in MpvPlayer except for __init__
        Copy is needed because subclassing via MpvPlayer._MpvPlayer__Listener doesn't work
        (even with name mangling)
        '''
        def __init__(self, playerController, playerIPCHandler, playerPath, filePath, args):
            """Fork: Remove real filepath checks and modifies command line arguments used"""
            self.playerIPCHandler = playerIPCHandler
            self.playerPath = playerPath
            self.mpv_arguments = playerController.getStartupArgs(args)
            self.mpv_running = True
            self.sendQueue = []
            self.readyToSend = True
            self.lastSendTime = None
            self.lastNotReadyTime = None
            self.__playerController = playerController
            if not self.__playerController._client._config["chatOutputEnabled"]:
                self.__playerController.alertOSDSupported = False
                self.__playerController.chatOSDSupported = False
            if self.__playerController.getPlayerPathErrors(playerPath, filePath):
                raise ValueError()

            if filePath:
                self.__playerController.delayedFilePath = filePath

            # At least mpv may output escape sequences which result in syncplay
            # trying to parse something like
            # "\x1b[?1l\x1b>ANS_filename=blah.mkv". Work around this by
            # unsetting TERM.
            env = os.environ.copy()
            if 'TERM' in env:
                del env['TERM']
            # On macOS, youtube-dl requires system python to run. Set the environment
            # to allow that version of python to be executed in the mpv subprocess.
            if isMacOS():
                try:
                    env['PATH'] = '/opt/homebrew/bin:/usr/local/bin:/usr/bin'
                    ytdl_path = subprocess.check_output(['which', 'youtube-dl'], text=True, env=env).rstrip('\n')
                    with open(ytdl_path, 'rb') as f:
                        ytdl_shebang = f.readline()
                    ytdl_python = ytdl_shebang.decode('utf-8').lstrip('!#').rstrip('\n')
                    if '/usr/bin/env' in ytdl_python:
                        python_name = ytdl_python.split(' ')[1]
                        python_executable = subprocess.check_output(['which', python_name], text=True, env=env).rstrip('\n')
                    else:
                        python_executable = ytdl_python
                    pythonLibs = subprocess.check_output([python_executable, '-E', '-c',
                                                          'import sys; print(sys.path)'],
                                                          text=True, env=dict())
                    pythonLibs = ast.literal_eval(pythonLibs)
                    pythonPath = ':'.join(pythonLibs[1:])
                except Exception as e:
                    pythonPath = None
                if pythonPath is not None:
                    env['PATH'] = python_executable + ':' + env['PATH']
                    env['PYTHONPATH'] = pythonPath
            try:
                socket = self.mpv_arguments.get('input-ipc-server')
                # Only these args work, others cause webtorrent to quit immediately
                # after opening mpv
                webtorrent_args = {
                    'filepath': filePath,
                    'player_args_dict': {}
                }
                self.mpvpipe = self.playerIPCHandler(mpv_location=self.playerPath, ipc_socket=socket, loglevel="info", log_handler=self.__playerController.mpv_log_handler, env=env, start_mpv=True, **webtorrent_args)
            except Exception as e:
                self.quitReason = getMessage("media-player-error").format(str(e)) + " " + getMessage("mpv-failed-advice")
                self.__playerController.reactor.callFromThread(self.__playerController._client.ui.showErrorMessage, self.quitReason, True)
                self.__playerController.drop()
            self.__process = self.mpvpipe
            #self.mpvpipe.show_text("HELLO WORLD!", 1000)
            threading.Thread.__init__(self, name="MPV Listener")

        # Everything below here is the same as mpv.py

        def __getCwd(self, filePath, env):
            if not filePath:
                return None
            if os.path.isfile(filePath):
                cwd = os.path.dirname(filePath)
            elif 'HOME' in env:
                cwd = env['HOME']
            elif 'APPDATA' in env:
                cwd = env['APPDATA']
            else:
                cwd = None
            return cwd

        def run(self):
            pass

        def sendChat(self, message):
            if message:
                if message[:1] == "/" and message != "/":
                    command = message[1:]
                    if command and command[:1] == "/":
                        message = message[1:]
                    else:
                        self.__playerController.reactor.callFromThread(
                            self.__playerController._client.ui.executeCommand, command)
                        return
                self.__playerController.reactor.callFromThread(self.__playerController._client.sendChat, message)

        def isReadyForSend(self):
            self.checkForReadinessOverride()
            return self.readyToSend

        def setReadyToSend(self, newReadyState):
            oldState = self.readyToSend
            self.readyToSend = newReadyState
            self.lastNotReadyTime = time.time() if newReadyState == False else None
            if self.readyToSend == True:
                self.__playerController._client.ui.showDebugMessage("<mpv> Ready to send: True")
            else:
                self.__playerController._client.ui.showDebugMessage("<mpv> Ready to send: False")
            if self.readyToSend == True and oldState == False:
                self.processSendQueue()

        def checkForReadinessOverride(self):
            if self.lastNotReadyTime and time.time() - self.lastNotReadyTime > constants.MPV_MAX_NEWFILE_COOLDOWN_TIME:
                self.setReadyToSend(True)

        def sendLine(self, line, notReadyAfterThis=None):
            self.checkForReadinessOverride()
            try:
                if self.sendQueue:
                    if constants.MPV_SUPERSEDE_IF_DUPLICATE_COMMANDS:
                        for command in constants.MPV_SUPERSEDE_IF_DUPLICATE_COMMANDS:
                            line_command = " ".join(line)
                            answer = line_command.startswith(command)
                            #self.__playerController._client.ui.showDebugMessage("Does line_command {} start with {}? {}".format(line_command, command, answer))
                            if line_command.startswith(command):
                                for itemID, deletionCandidate in enumerate(self.sendQueue):
                                    if " ".join(deletionCandidate).startswith(command):
                                        self.__playerController._client.ui.showDebugMessage(
                                            "<mpv> Remove duplicate (supersede): {}".format(self.sendQueue[itemID]))
                                        try:
                                            self.sendQueue.remove(self.sendQueue[itemID])
                                        except UnicodeWarning:
                                            self.__playerController._client.ui.showDebugMessage(
                                                "<mpv> Unicode mismatch occurred when trying to remove duplicate")
                                            # TODO: Prevent this from being triggered
                                            pass
                                        break
                            break
                    if constants.MPV_REMOVE_BOTH_IF_DUPLICATE_COMMANDS:
                        for command in constants.MPV_REMOVE_BOTH_IF_DUPLICATE_COMMANDS:
                            if line == command:
                                for itemID, deletionCandidate in enumerate(self.sendQueue):
                                    if deletionCandidate == command:
                                        self.__playerController._client.ui.showDebugMessage(
                                            "<mpv> Remove duplicate (delete both): {}".format(self.sendQueue[itemID]))
                                        self.__playerController._client.ui.showDebugMessage(self.sendQueue[itemID])
                                        return
            except Exception as e:
                self.__playerController._client.ui.showDebugMessage("<mpv> Problem removing duplicates, etc: {}".format(e))
            self.sendQueue.append(line)
            self.processSendQueue()
            if notReadyAfterThis:
                self.setReadyToSend(False)

        def processSendQueue(self):
            while self.sendQueue and self.readyToSend:
                if self.lastSendTime and time.time() - self.lastSendTime < constants.MPV_SENDMESSAGE_COOLDOWN_TIME:
                    self.__playerController._client.ui.showDebugMessage(
                        "<mpv> Throttling message send, so sleeping for {}".format(
                            constants.MPV_SENDMESSAGE_COOLDOWN_TIME))
                    time.sleep(constants.MPV_SENDMESSAGE_COOLDOWN_TIME)
                try:
                    lineToSend = self.sendQueue.pop()
                    if lineToSend:
                        self.lastSendTime = time.time()
                        self.actuallySendLine(lineToSend)
                except IndexError:
                    pass

        def stop_client(self):
            self.readyToSend = False
            try:
                self.mpvpipe.terminate()
            except: #When mpv is already closed
                pass
            self.__playerController._takeLocksDown()
            self.__playerController.reactor.callFromThread(self.__playerController._client.stop, False)

        def actuallySendLine(self, line):
            try:
                self.__playerController._client.ui.showDebugMessage("player >> {}".format(line))
                try:
                    self.mpvpipe.command(*line)
                except Exception as e:
                    self.__playerController._client.ui.showDebugMessage("CANNOT SEND {} DUE TO {}".format(line, e))
                    self.stop_client()
            except IOError:
                pass

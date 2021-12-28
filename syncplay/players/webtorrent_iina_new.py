import os
import threading
import subprocess
import ast
import time
from syncplay import constants
from syncplay.utils import findResourcePath, isMacOS, findWorkingDir
from syncplay.players.mpv import MpvPlayer
from syncplay.players.webtorrent_iina_ipc import WEBTORRENT_IINA
from syncplay.messages import getMessage

class WebtorrentIinaPlayer(MpvPlayer):

    @staticmethod
    def run(client, playerPath, filePath, args):
            constants.MPV_NEW_VERSION = True
            constants.MPV_OSC_VISIBILITY_CHANGE_VERSION = True
            # "player" path is actually webtorrent (which uses mpv)
            if isMacOS():
                node_path = os.path.join(findWorkingDir(), 'node', 'bin', 'node')
                webtorrent_path = os.path.join(findWorkingDir(), 'webtorrent-cli', 'bin', 'cmd.js')
                playerPath = f'{node_path} {webtorrent_path}'
            else:
                playerPath = client._config['webtorrentPath']
            return WebtorrentIinaPlayer(client, WebtorrentIinaPlayer.getExpandedPath(playerPath), filePath, args)

    def _loadFile(self, filePath):
        # basically temp no-op for now
        self._clearFileLoaded()
        # TODO load another magnet

    @staticmethod
    def getStartupArgs(userArgs):
        args = {}
        if userArgs:
            for argToAdd in userArgs:
                if argToAdd.startswith('--'):
                    argToAdd = argToAdd[2:]
                elif argToAdd.startswith('-'):
                    argToAdd = argToAdd[1:]
                if argToAdd.strip() == "":
                    continue
                if "=" in argToAdd:
                    (argName, argValue) = argToAdd.split("=", 1)
                else:
                    argName = argToAdd
                    argValue = "yes"
                args[argName] = argValue
        return args

    @staticmethod
    def getDefaultPlayerPathsList():
        l = []
        for path in constants.IINA_PATHS:
            p = WebtorrentIinaPlayer.getExpandedPath(path)
            if p:
                l.append(p)
        return l

    @staticmethod
    def isValidPlayerPath(path):
        if "iina-cli" in path or "iina-cli" in WebtorrentIinaPlayer.getExpandedPath(path):
            return True
        return False

    @staticmethod
    def getExpandedPath(playerPath):
        if "iina-cli" in playerPath:
            pass
        elif "IINA.app/Contents/MacOS/IINA" in playerPath:
            playerPath = os.path.join(os.path.dirname(playerPath), "iina-cli")
        
        if os.access(playerPath, os.X_OK):
            return playerPath
        for path in os.environ['PATH'].split(':'):
            path = os.path.join(os.path.realpath(path), playerPath)
            if os.access(path, os.X_OK):
                return path  
        return playerPath

    @staticmethod
    def getIconPath(path):
        return constants.IINA_ICONPATH

    def __init__(self, client, playerPath, filePath, args):
        from twisted.internet import reactor
        self.reactor = reactor
        self._client = client
        self._set_defaults()

        self._playerIPCHandler = WEBTORRENT_IINA
        self._create_listener(playerPath, filePath, args)
      
    def _preparePlayer(self):
        for key, value in constants.IINA_PROPERTIES.items():
            self._setProperty(key, value)
        self._listener.sendLine(["load-script", findResourcePath("syncplayintf.lua")])
        super()._preparePlayer()

    def _onFileUpdate(self):
        # do not show file info for our placeholder image in Syncplay UI
        if self._filename == "iina-bkg.png":
            return
        else:
            super()._onFileUpdate()

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

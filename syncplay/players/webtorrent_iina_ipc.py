import os
import time
import subprocess

from syncplay.players.ipc_iina import IINA, IINAProcess
from syncplay.vendor.python_mpv_jsonipc.python_mpv_jsonipc import log, MPVError

#from syncplay.utils import resourcespath

class WEBTORRENT_IINA(IINA):
    def _start_mpv(self, ipc_socket, mpv_location, **kwargs):
        '''Fork: Renames IINAProcess -> WEBTORRENT_IINAProcess'''
        # Attempt to start IINA 3 times.
        for i in range(3):
            try:
                self.mpv_process = WEBTORRENT_IINAProcess(ipc_socket, mpv_location, **kwargs)
                break
            except MPVError:
                log.warning("IINA start failed.", exc_info=1)
                continue
        else:
            raise MPVError("IINA process retry limit reached.")

class WEBTORRENT_IINAProcess(IINAProcess):
    def _start_process(self, ipc_socket, args, env):
        '''Exactly the same except for shell=True for some reason'''
        self.process = subprocess.Popen(args, env=env, shell=True)
        ipc_exists = False
        # IINA needs more time to launch
        time.sleep(5)
        for _ in range(100): # Give MPV 10 seconds to start.
            time.sleep(0.1)
            self.process.poll()
            if os.path.exists(ipc_socket):
                ipc_exists = True
                log.debug("Found IINA socket.")
                break
            if self.process.returncode != 0: # iina-cli returns immediately after its start
                log.error("IINA failed with returncode {0}.".format(self.process.returncode))
                break
        else:
            self.process.terminate()
            raise MPVError("IINA start timed out.")

        # returncode is still None for me, even when ipc exists
        if not ipc_exists or self.process.returncode is not None:
            self.process.terminate()
            raise MPVError("IINA not started.")

    def _get_arglist(self, exec_location, **kwargs):
        '''Adapt to shell=True and the download command'''
        args = [
            exec_location, 'download', f'"{kwargs["filepath"]}"', '--iina', '--playlist',
            '--quiet'
        ]
        player_args_dict = kwargs['player_args_dict']
        # IINA appends mpv based commands with `mpv`
        self._set_default(player_args_dict, "mpv-input-ipc-server", self.ipc_socket)
        player_args = ' '.join(
            ["--{0}={1}".format(v[0].replace("_", "-"), self._mpv_fmt(v[1]))
             for v in player_args_dict.items()]
        )
        # 'iina-bkg.png' not needed here, as iina is not started without a file
        args.append(f'--player-args="{player_args} --no-stdin"')
        args = ' '.join(args)
        return args

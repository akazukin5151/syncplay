import subprocess
import time
import os

from syncplay.vendor.python_mpv_jsonipc.python_mpv_jsonipc import log, MPV, MPVError, MPVProcess

class WEBTORRENT(MPV):
    def _start_mpv(self, ipc_socket, mpv_location, **kwargs):
        '''Exactly the same but MPVProcess -> WEBTORRENTProccess'''
        # Attempt to start MPV 3 times.
        for i in range(3):
            try:
                self.mpv_process = WEBTORRENTProccess(ipc_socket, mpv_location, **kwargs)
                break
            except MPVError:
                log.warning("MPV start failed.", exc_info=1)
                continue
        else:
            raise MPVError("MPV process retry limit reached.")


class WEBTORRENTProccess(MPVProcess):
    def _start_process(self, ipc_socket, args, env):
        '''Exactly the same except for shell=True for some reason'''
        self.process = subprocess.Popen(args, env=env, shell=True)
        ipc_exists = False
        for _ in range(100): # Give MPV 10 seconds to start.
            time.sleep(0.1)
            self.process.poll()
            if os.path.exists(ipc_socket):
                ipc_exists = True
                log.debug("Found MPV socket.")
                break
            if self.process.returncode is not None:
                log.error("MPV failed with returncode {0}.".format(self.process.returncode))
                break
        else:
            self.process.terminate()
            raise MPVError("MPV start timed out.")

        if not ipc_exists or self.process.returncode is not None:
            self.process.terminate()
            raise MPVError("MPV not started.")

    def _get_arglist(self, exec_location, **kwargs):
        '''Adapt to shell=True and the download command'''
        args = [
            exec_location, 'download', f'"{kwargs["filepath"]}"', '--mpv', '--playlist',
            '--quiet'
        ]
        player_args_dict = kwargs['player_args_dict']
        self._set_default(player_args_dict, "input_ipc_server", self.ipc_socket)
        player_args = ' '.join(
            ["--{0}={1}".format(v[0].replace("_", "-"), self._mpv_fmt(v[1]))
             for v in player_args_dict.items()]
        )
        args.append(f'--player-args="{player_args}"')
        args = ' '.join(args)
        return args

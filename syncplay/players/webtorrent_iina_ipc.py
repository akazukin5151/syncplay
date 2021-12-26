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
#    def _get_arglist(self, exec_location, **kwargs):
#        args = [exec_location]
#        args.append('--no-stdin')
#        args.append(resourcespath + 'iina-bkg.png')
#        self._set_default(kwargs, "mpv-input-ipc-server", self.ipc_socket)
#        args.extend("--{0}={1}".format(v[0].replace("_", "-"), self._mpv_fmt(v[1]))
#                    for v in kwargs.items())
#        return args

    def _get_arglist(self, exec_location, **kwargs):
        '''Adapt to shell=True and the download command'''
        args = [
            exec_location, 'download', f'"{kwargs["filepath"]}"', '--iina', '--playlist',
            '--quiet'
        ]
        player_args_dict = kwargs['player_args_dict']
        self._set_default(player_args_dict, "input_ipc_server", self.ipc_socket)
        player_args = ' '.join(
            ["--{0}={1}".format(v[0].replace("_", "-"), self._mpv_fmt(v[1]))
             for v in player_args_dict.items()]
        )
        # 'iina-bkg.png' not needed here, as iina is not started without a file
        args.append(f'--player-args="{player_args} --no-stdin"')
        args = ' '.join(args)
        return args

import subprocess

class WebtorrentClient:
    def __init__(self, webtorrent_path, magnet):
        self.webtorrent_path = webtorrent_path
        self.magnet = magnet

    def start(self):
        self.launch_webtorrent()
        self.filepaths = self.get_leeching_file()

    def launch_webtorrent(self):
        args = f'{self.webtorrent_path} "{self.magnet}"'
        print(f"Launching webtorrent with {args=}")
        self.process = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def get_leeching_file(self):
        while True:
            stdout = self.process.stdout.readline()
            decoded = stdout.decode('utf-8')
            print(decoded, end='')
            marker = 'allHrefs: '
            if marker in decoded:
                res = decoded[len(marker):].replace('\"', '').replace('\n', '').split(',')
                print(f'parsed {res=}')
                # could wait a while to increase the chance that when loading
                # the file, the video will immediately play
                # but it's not necessary, mpv will reload automatically
                # the problem is just that there is no user feedback to the torrent
                # progress. a sleep of 10 seconds opens up possibilities
                # to provide a fake 10s progress bar
                #print('waiting 10 s')
                #time.sleep(10)
                return res

    def stop(self):
        self.process.terminate()

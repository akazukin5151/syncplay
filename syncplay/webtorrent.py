import json
import time
import subprocess
from urllib.request import urlopen, Request

class WebtorrentClient:
    def __init__(self, webtorrent_path, magnet):
        self.webtorrent_path = webtorrent_path
        self.magnet = magnet.replace('\n', '')

    def start(self):
        self.launch_webtorrent()
        self.get_filenames_in_torrent()
        self.filepaths = self.get_leeching_file()

    def launch_webtorrent(self):
        self.process = subprocess.Popen(self.webtorrent_path, shell=True)
        # Needs some time for the HTTP server to start
        time.sleep(2)

    # filenames in torrent need to be processed to paths for player
    def get_filenames_in_torrent(self):
        req = Request(f'http://localhost:8080/metainfo?magnet={self.magnet}')
        req.add_header('accept', 'application/json')
        res = urlopen(req)
        html_bytes = res.read()
        html = html_bytes.decode('utf-8')
        j = json.loads(html)
        self.torrent_filenames = [name for name in j['paths'] if name != '']

    # this should be _for_player
    def get_leeching_file(self):
        base = f'http://localhost:8080/data?magnet={self.magnet}'
        if self.torrent_filenames == []:
            return [base]
        return [
            f'{base}&path={filename}'
            for filename in self.torrent_filenames
        ]

    def stop(self):
        self.process.terminate()

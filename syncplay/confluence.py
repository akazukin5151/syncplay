import json
import time
import subprocess
from urllib.request import urlopen, Request

class ConfluenceClient:
    def __init__(self, confluence_path, magnet, download_dir):
        self.confluence_path = confluence_path
        self.download_dir = download_dir
        self.magnet = magnet.replace('\n', '')

    def start(self):
        self.launch_confluence()
        self.torrent_filenames = self.get_filenames_in_torrent()
        self.filepaths = self.get_leeching_files_for_player()

    def launch_confluence(self):
        args = f'{self.confluence_path}'
        if self.download_dir is not None:
            args += f' -fileDir="{self.download_dir}"'
        self.process = subprocess.Popen(args, shell=True)
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
        return [name for name in j['paths'] if name != '']

    def get_leeching_files_for_player(self):
        base = f'http://localhost:8080/data?magnet={self.magnet}'
        if self.torrent_filenames == []:
            return [base]
        return [
            f'{base}&path={filename}'
            for filename in self.torrent_filenames
        ]

    def stop(self):
        self.process.terminate()

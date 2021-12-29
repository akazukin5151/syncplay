import random
import socket
import json
import subprocess

class WebtorrentClient:
    def __init__(self, webtorrent_path, magnet):
        self.webtorrent_path = webtorrent_path
        self.magnet = magnet
        self.socket_address = f'/tmp/webtorrent_{random.randint(0, 2**48)}'
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.socket_address)
        self.socket.listen()

    def start(self):
        self.launch_webtorrent()
        self.filepath = self.get_leeching_file()

    def launch_webtorrent(self):
        args = f'{self.webtorrent_path} download "{self.magnet}" --ipc="{self.socket_address}" --quiet --keep-seeding'
        print(f"Launching webtorrent with {args=}")
        subprocess.Popen(args, shell=True)

    def get_leeching_file(self):
        self.conn, addr = self.socket.accept()
        while True:
            data = self.conn.recv(1024)
            if not data:
                return None
            # remove trailing `\x0c`
            decoded = data.decode('utf-8')[:-1]
            j = json.loads(decoded)
            if j['type'] == 'href':
                return j['data'].replace('"', '')

    def stop(self):
        self.conn.close()
        # webtorrent will close on socket close too
        self.socket.close()

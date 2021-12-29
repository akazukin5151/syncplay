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
        args = f'{self.webtorrent_path} "{self.magnet}" "{self.socket_address}"'
        print(f"Launching webtorrent with {args=}")
        subprocess.Popen(args, shell=True)

    def get_leeching_file(self):
        self.conn, addr = self.socket.accept()
        while True:
            data = self.conn.recv(1024)
            if not data:
                return None
            # handle data having multiple lines separated by `\x0c`
            lines = data.split(b'\x0c')
            for line in lines:
                if line == b'':
                    continue
                decoded = line.decode('utf-8')
                j = json.loads(decoded)
                if j['type'] == 'href':
                    return j['data'].replace('"', '')
                elif j['type'] == 'hrefs_begin':
                    filepaths = []
                elif j['type'] == 'hrefs':
                    filepaths.append(j['data'].replace('"', ''))
                elif j['type'] == 'hrefs_end':
                    return filepaths

    def stop(self):
        self.conn.close()
        # webtorrent will close on socket close too
        self.socket.close()
import syncplay.players


class PlayerFactory(object):
    def __init__(self):
        self._players = syncplay.players.getAvailablePlayers()
        self._torrent_players =self._players

    def getAvailablePlayerPaths(self):
        l = []
        for player in self._players:
            l.extend(player.getDefaultPlayerPathsList())
        return l

    def getAvailableTorrentPlayerPaths(self):
        l = []
        for player in self._torrent_players:
            l.extend(player.getDefaultPlayerPathsList())
        return l

    def getPlayerByPath(self, path):
        for player in self._players:
            if player.isValidPlayerPath(path):
                return player

    def getTorrentPlayerByPath(self, path):
        for player in self._torrent_players:
            if player.isValidPlayerPath(path):
                return player

    def getPlayerIconByPath(self, path):
        for player in self._players:
            if player.isValidPlayerPath(path):
                return player.getIconPath(path)
        return None

    def getTorrentPlayerIconByPath(self, path):
        for player in self._torrent_players:
            if player.isValidPlayerPath(path):
                return player.getIconPath(path)
        return None

    def getExpandedPlayerPathByPath(self, path):
        for player in self._players:
            if player.isValidPlayerPath(path):
                return player.getExpandedPath(path)
        return None

    def getExpandedTorrrentPlayerPathByPath(self, path):
        for player in self._torrent_players:
            if player.isValidPlayerPath(path):
                return player.getExpandedPath(path)
        return None

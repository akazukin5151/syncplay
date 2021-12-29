# Webtorrent-syncplay

This is a "fork" of webtorrent-cli that is only for syncplay. In particular it only supports streaming, returning the stream address (somewhere in localhost) through IPC.

It's not really a fork because it basically just uses webtorrent (the underlying library that powers both) in the same structure as webtorrent-cli, but those pieces were unchanged, so I want to maintain credit to the upstream code.

### License

MIT. Copyright (c) [Feross Aboukhadijeh](https://feross.org) and [WebTorrent, LLC](https://webtorrent.io).

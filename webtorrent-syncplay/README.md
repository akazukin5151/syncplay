# Webtorrent-syncplay

This is a "fork" of webtorrent-cli that is only for syncplay. In particular it only supports streaming, returning the stream address (somewhere in localhost) through IPC.

It's not really a fork because it basically just uses webtorrent (the underlying library that powers both) in the same structure as webtorrent-cli, but those pieces were unchanged, so I want to maintain credit to the upstream code.

## Install

Install with npm, or install node, symlink this dir to `~/.local/share`, and symlink `bin/  ` to `~/.local/bin/webtorrent-syncplay`

## Run

`webtorrent-syncplay magnet socket_address`

Where `magnet` is the magnet link and `socket_address` is the path to the IPC socket

## IPC API

The IPC connection will be used to send the path of the files being streamed through webtorrent. There are 3 types of data:

- type: `href`
    - data :: string
    - data is the filepath, which can be directly loaded into any video player
- type: `hrefs_begin`
    - data :: ()
    - No data sent; this is a marker signalling that the listener should expect to receive multiple filepaths as above
- type: `hrefs_end`
    - data :: ()
    - No data sent; this is a marker signalling that `hrefs_begin` has ended and all filepaths have been sent.

## License

MIT. Copyright (c) [Feross Aboukhadijeh](https://feross.org) and [WebTorrent, LLC](https://webtorrent.io).

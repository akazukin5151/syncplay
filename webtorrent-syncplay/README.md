# Webtorrent-syncplay

This is a "fork" of webtorrent-cli that is only for syncplay. In particular it only supports streaming, returning the stream address (served through an http server through localhost; actual file is in /tmp/webtorrent/) through stdout.

It's not really a fork because it basically just uses webtorrent (the underlying library that powers both) in the same structure as webtorrent-cli, but those pieces were unchanged, so I want to maintain credit to the upstream code.

## Install

Install with npm: `npm ci` to install dependencies then `npm i -g` to copy the script

Or install node, `npm ci` to install dependencies, symlink this dir to `~/.local/share`, and symlink `bin/` to `~/.local/bin/webtorrent-syncplay`

## Run

`webtorrent-syncplay magnet`

Where `magnet` is the magnet link

## Responses

Stdout will be used to send the path of the files being streamed through webtorrent. Wait for the line beginning with `allHrefs: `. It is followed by a list of double-quoted strings separated by commas, for example:

`allHrefs: "http://localhost:8000/0/{file1}","http://localhost:8000/0/{file2}"`

## License

MIT. Copyright (c) [Feross Aboukhadijeh](https://feross.org) and [WebTorrent, LLC](https://webtorrent.io).

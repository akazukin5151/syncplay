<!---
# Copyright (C) 2019 Syncplay
# This file is licensed under the MIT license - http://opensource.org/licenses/MIT

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
-->

# Fork

This is a fork of Syncplay that adds support for streaming videos in torrents. Stream a magnet link in real-time, synchronised with your friends.

For torrenting, only mpv is supported on Linux. mpv and IINA is supported on macOS. Windows is not supported. Non-torrent features are maintained, so this can function as a perfect replacement for upstream Syncplay.

## Install for macOS

1. Download the `.dmg` in the latest successful CI action and install as normal

## Install for Linux from AppImage

1. Download the AppImage from the latest successful CI action

Note: AppImage doesn't work for Fedora due to broken dynamic linking of PySide2 by conda-forge, see [upstream issue 355](github.com/Syncplay/syncplay/issues/355)

## Install from source

0. Prerequisites: Go >= 1.17 and Python
1. Git clone and cd
2. `git submodule update --init` to clone the confluence fork
3. `cd vendor/confluence` then `go build -o out/confluence`
4. Install syncplay however you want. For development, you could use `pip install -e .`. Make sure to disable anaconda before running that, and remove any existing executables in `~/.local/bin`.

## First time setup

1. Open Syncplay
2. (Linux only) Fill the path to the confluence binary you installed above (eg, `/some/path/here/syncplay/vendor/confluence/out/confluence`)
3. Use a compatible media player
    - Linux: mpv only
    - macOS: IINA or mpv
4. Optionally, check "show more settings" and go to the Misc Tab, and set a torrent download path. This is where torrents will be downloaded to.

## Usage

1. Tick the "Video is a magnet link" checkbox
2. Paste in the magnet to the `Magnet link` field
    - Alternatively, if you have a link to a webpage containing a magnet, click `From URL` to try to automatically fetch the magnet from the page
3. (Choose a server and room and stuff, then) (click the) run Syncplay (button)
4. Wait a while for it to buffer
5. Everyone in the room should repeat the above steps, with the same magnet link
6. Another magnet link can be used to replace the current video in `File` -> `Stream magnet link` or `File` -> `Stream magnet from webpage`

### OS support

Focusing on Linux and macOS for now because I use Linux and my friend uses a Mac. I have no problem in entering a few commands on the terminal, and I suspect most Linux users feel the same, so there's not much benefit for the tight bundling of node and confluence for Linux. Torrenting for Windows won't be supported until we have a need (or you submit a PR)

### Video player support

Focusing on mpv and IINA because that's what we use too. There is no technical barrier to supporting other video players, but I do not have the capacity to test and support all of them. You're welcome to open a PR and maintain your changes.

### Design decisions

Changes in this fork aims to affect upstream contents as minimal as possible. That does not mean always creating new files however, but just in an appropriate manner and not a hacky manner. This is how it can maintain compatibility with upstream Syncplay and is perfectly usable as a drop-in replacement.

Originally, [webtorrent](https://github.com/webtorrent/webtorrent) was used as the backend torrent client. However, being dependent on Javascript was a major problem because it necessitated users to either install Node.js and my script, or bundling node and the script into the `.app`, which ballooned its size to 200 MB. Furthermore, the Javascript ecosystem extensively depends on lots of tiny dependencies. Even after removing every dependency but webtorrent itself, there were still 50 dependencies. 50 packages to read through for security and code reviews.

There was a clear need for an alternative in a statically typed language. [anacrolix/confluence](https://github.com/anacrolix/confluence), based on [anacrolix/torrent](https://github.com/anacrolix/torrent) was actively maintained, well documented, and supports a HTTP server (which was necessary for video players to request specific pieces to respond to user seeks, instead of streaming everything sequentially). Go is not my favourite language, but at least it gives more static guarantees than Javascript and compiles to a smaller and more portable binary. It still dynamically links to system libraries in C, but it has reduced the size of the `.app` back to 100 MB. The fork is located [here](https://github.com/akazukin5151/confluence) and has minor changes to reduce the need of further Python dependencies (it already depends on a bencode library, so might as well decode bencode in Go to a string).

# Syncplay
![GitHub Actions build status](https://github.com/Syncplay/syncplay/workflows/Build/badge.svg)

Solution to synchronize video playback across multiple instances of mpv, VLC, MPC-HC, MPC-BE and mplayer2 over the Internet.

## Official website
https://syncplay.pl

## Download
https://syncplay.pl/download/

## What does it do

Syncplay synchronises the position and play state of multiple media players so that the viewers can watch the same thing at the same time.
This means that when one person pauses/unpauses playback or seeks (jumps position) within their media player then this will be replicated across all media players connected to the same server and in the same 'room' (viewing session).
When a new person joins they will also be synchronised. Syncplay also includes text-based chat so you can discuss a video as you watch it (or you could use third-party Voice over IP software to talk over a video).

## What it doesn't do

Syncplay is not a file sharing service.

## License

This project, the Syncplay released binaries, and all the files included in this repository unless stated otherwise in the header of the file, are licensed under the [Apache License, version 2.0](https://www.apache.org/licenses/LICENSE-2.0.html). A copy of this license is included in the LICENSE file of this repository. Licenses and attribution notices for third-party media are set out in [third-party-notices.txt](syncplay/resources/third-party-notices.txt).

## Authors
* *Initial concept and core internals developer* - Uriziel.
* *GUI design and current lead developer* - Et0h.
* *Original SyncPlay code* - Tomasz Kowalczyk (Fluxid), who developed SyncPlay at https://github.com/fluxid/syncplay
* *Other contributors* - See http://syncplay.pl/about/development/

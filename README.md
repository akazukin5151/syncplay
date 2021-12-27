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

This is a fork of Syncplay that adds support for [webtorrent](https://github.com/webtorrent/webtorrent-cli).

For tormenting, only mpv is supported on Linux. mpv and IINA is supported on macOS. Windows is not supported. Non-torrent features are maintained, so this can function as a perfect replacement for upstream Syncplay.

## Install for macOS

1. Download the `.dmg` in the latest successful CI action and install as normal

## Install for Linux

1. Install `webtorrent-cli` using the link above
2. Clone this repo and install from source as normal

## Usage

1. Open Syncplay, tick the "Torrent mode" checkbox
2. (Linux only) Fill the path to the webtorrent script you installed above
3. Select your media player
    - Linux: Fill in the path to mpv (eg `/usr/bin/mpv`)
    - macOS: Use the dropdown to select either IINA or mpv
4. (Choose a server and room and stuff, then) (click the) run Syncplay (button)
5. Go to `File` -> `Open media stream URL` and paste in your magnet link (`magnet:...`)
    - Can also paste in the magnet in the `Path to video` field between steps 3 and 4.
6. Wait a while for it to buffer
7. Everyone in the room should repeat the above steps, with the same magnet link

Focusing on Linux and macOS for now because I use Linux and my friend uses a Mac. I have no problem in entering a few commands on the terminal, and I suspect most Linux users feel the same, so there's not much benefit for the tight bundling of node and webtorrent for Linux. Torrenting for Windows won't be supported until we have a need (or you submit a PR)

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

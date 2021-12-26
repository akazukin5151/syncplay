Note: this is all for testing and the Syncplay app does *not* yet use those dependencies. Follow the instructions in the README

# webtorrent-cli fork

## Setup

Clone the fork with:

`git submodule update --init`

## How to use this to build Syncplay?

Run `npm install` inside the directory before building the mac app

Building the mac app (`python3 buildPy2app.py py2app`) will include the entire submodule into the `.app`. See the CI workflow for more info

## Why vendor this?

Webtorrent-cli is a required dependency to use the torrent streaming feature. It has been vendored (source code & executable copied) here so that upon installation of Syncplay, webtorrent-cli would be installed as well.

This is because the only installation for webtorrent-cli is using npm, which in turn requires node.js to be installed. This is only feasible for user-developers who either already have npm or are willing to compile everything from source manually.

For those who don't want to, the vendored webtorrent-cli lets them use the app without any further installation.

## Why fork this?

- Fix mpv command for macOS
- Move mpv's `--term-title-msg` argument there because it is otherwise impossible to escape shell expansion yet un-escape it so that mpv can understand it.

# Node LTS (version 16.13.1)

## Setup

No setup needed. Would need to manually update to the next LTS though.

## How to use this to build Syncplay?

Run `unzip_node_mac.sh` before building the mac app (`python3 buildPy2app.py py2app`). See the CI workflow for more info

## Why vendor this?

- Webtorrent-cli is written in Javascript (node.js), so requires the node interpreter to run
- It uses ES Modules, but `pkg`, `ncc`, `webpack`, `esbuild`, `bunchee` etc do not support ES Modules
- Changing the import statements to `require` functions work, but involves increased maintenance burden
- The node interpreter is just 4 KB in size

## Why should I trust your archive?

You can download the archive of the binary yourself from https://nodejs.org/en/download/

## Do you realize what you're doing?

I know right, imagine needing to download an entire programming language just to run a program! Dynamic, un-compiled languages will always remain dynamic, un-compiled languages; people will always be able to take advantage of their flexibility to undermine any later attempts at putting on band-aids.

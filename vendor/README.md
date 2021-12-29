Note that these vendored dependencies are only used in the macOS CI. Linux users need to specify the path to their webtorrent installation anyway, and it is up to them to ensure it can be executed without needing to call node (eg, `webtorrent-syncplay` and not `node cmd.js`). The node dependency here is thus irrelevant for Linux.

# Node.js LTS (version 16.13.1)

## Setup

No setup needed. Would need to manually update to the next LTS though.

## How to use this to build Syncplay?

Run `unzip_node_mac.sh` before building the mac app (`python3 buildPy2app.py py2app`). See the CI workflow for more info

## Why vendor this?

- Webtorrent-syncplay is written in Javascript (node.js), so requires the node interpreter to run
- It uses ES Modules, but `pkg`, `ncc`, `webpack`, `esbuild`, `bunchee` etc do not support ES Modules
- Changing the import statements to `require` functions work, but involves increased maintenance burden
- The node interpreter is just 4 KB in size

## Why should I trust your archive?

You can download the archive of the binary yourself from https://nodejs.org/en/download/

## Do you realize what you're doing?

I know right, imagine needing to download an entire programming language just to run a program! Dynamic, un-compiled languages will always remain dynamic, un-compiled languages; people will always be able to take advantage of their flexibility to undermine any later attempts at putting on band-aids.

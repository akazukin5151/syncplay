#!/usr/bin/env node
import WebTorrent from 'webtorrent'

let client

process.on('SIGINT', gracefulExit)
process.on('SIGTERM', gracefulExit)

let argv = process.argv.slice(2)
const magnet = argv[0]

console.log(`webtorrent: got magnet ${magnet}`)

if (!magnet) {
  console.log('magnet is missing!')
  process.exit(1)
}

runDownload(magnet)

async function runDownload (magnet) {
  if (!argv.out && !argv.stdout) {
    argv.out = process.cwd()
  }

  client = new WebTorrent({
//    torrentPort: argv['torrent-port'],
//    dhtPort: argv['dht-port'],
//    downloadLimit: argv.downloadLimit,
//    uploadLimit: argv.uploadLimit
  })
  client.on('error', fatalError)

  const torrent = client.add(magnet, {
//    path: argv.out,
//    announce: argv.announce
  })

  torrent.on('infoHash', () => {
    if ('select' in argv) {
      torrent.so = argv.select.toString()
    }

    updateMetadata()
    torrent.on('wire', updateMetadata)

    function updateMetadata () {
      console.log(`webtorrent: fetching torrent metadata from ${torrent.numPeers} peers`)
    }

    torrent.on('metadata', () => {
      torrent.removeListener('wire', updateMetadata)

      console.log('webtorrent: verifying existing torrent data...')
    })
  })

  torrent.on('done', () => {
    const numActiveWires = torrent.wires.reduce((num, wire) => num + (wire.downloaded > 0), 0)

    console.log(`webtorrent: torrent downloaded successfully from ${numActiveWires}/${torrent.numPeers} peers in ${getRuntime()}s!`)
  })

  // Start http server
  const server = torrent.createServer()

  server.listen(8000)
    .on('error', err => {
      if (err.code === 'EADDRINUSE' || err.code === 'EACCES') {
        // If port is taken, pick one a free one automatically
        server.close()
        const serv = server.listen(0)
        argv.port = server.address().port
        return serv
      } else return fatalError(err)
    })

  server.once('listening', initServer)
  server.once('connection', () => console.log('webtorrent: serving connection...'))

  function initServer () {
    if (torrent.ready) {
      onReady()
    } else {
      torrent.once('ready', onReady)
    }
  }

  async function onReady () {
    let base = `http://localhost:${server.address().port}`
    let allHrefs = []
    torrent.files.forEach((file, i) =>
      allHrefs.push(JSON.stringify(`${base}/${i}/${encodeURIComponent(file.name)}`))
    )
    console.log(`allHrefs: ${allHrefs}`)
  }
}

function fatalError (err) {
  console.log(`webtorrent Error: ${err.message || err}`)
  process.exit(1)
}

function gracefulExit () {
  console.log('webtorrent webtorrent is exiting...')

  process.removeListener('SIGINT', gracefulExit)
  process.removeListener('SIGTERM', gracefulExit)

  if (!client) {
    return
  }

  client.destroy(err => {
    if (err) {
      return fatalError(err)
    }

    // Quit after 1 second. This is only necessary for `webtorrent-hybrid` since
    // the `electron-webrtc` keeps the node process alive quit.
    setTimeout(() => process.exit(0), 1000)
      .unref()
  })
}

function getRuntime () {
  return Math.floor((Date.now() - argv.startTime) / 1000)
}


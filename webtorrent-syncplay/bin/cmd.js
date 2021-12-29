#!/usr/bin/env node
import WebTorrent from 'webtorrent'
import ipc from 'node-ipc'

let client, server

let expectedError = false

process.on('exit', code => {
  if (code === 0 || expectedError) return // normal exit
  if (code === 130) return // intentional exit with Control-C
})

process.on('SIGINT', gracefulExit)
process.on('SIGTERM', gracefulExit)

let argv = process.argv.slice(2)
let magnet = argv[0]
let socket_address = argv[1]

console.log(`webtorrent: got magnet ${magnet}`)
console.log(`webtorrent: got socket_address ${socket_address}`)

if (!magnet || !socket_address) {
    console.log('magnet or socket_address is missing!')
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

      console.log(`webtorrent: verifying existing torrent data...`)
    })
  })

  torrent.on('done', () => {
    const numActiveWires = torrent.wires.reduce((num, wire) => num + (wire.downloaded > 0), 0)

    console.log(`webtorrent: torrent downloaded successfully from ${numActiveWires}/${torrent.numPeers} peers in ${getRuntime()}s!`)
  })

  // Start http server
  server = torrent.createServer()

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
    let href = `http://localhost:${server.address().port}`
    let allHrefs = []
    let emitter
    if (torrent.files.length > 1) {
      torrent.files.forEach((file, i) =>
        allHrefs.push(JSON.stringify(`${href}/${i}/${encodeURIComponent(file.name)}`))
      )
      emitter = () => {
        ipc.of.myid.emit('hrefs_begin')
        allHrefs.forEach(href => ipc.of.myid.emit('hrefs', href))
        ipc.of.myid.emit('hrefs_end')
      }
    } else {
      href += `/0/${encodeURIComponent(torrent.files[0].name)}`
      emitter = () => ipc.of.myid.emit('href', href)
    }

    ipc.connectTo('myid', socket_address, () => {
      ipc.of.myid.on('connect', emitter)
      ipc.of.myid.on('disconnect', () => {
          ipc.disconnect('myid')
          gracefulExit()
      })
    })
  }
}

function fatalError (err) {
  console.log(`webtorrent Error: ${err.message || err}`)
  process.exit(1)
}

function gracefulExit () {
  console.log(`webtorrent webtorrent is exiting...`)

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


#!/usr/bin/env node
import { createReadStream } from 'node:fs'
import fs from 'node:fs/promises'
import { fileURLToPath, pathToFileURL } from 'node:url'
import path from 'node:path'
import { spawn } from 'node:child_process'

const root = path.dirname(fileURLToPath(import.meta.url))
const usage = `Usage: node map-previewer/preview.mjs [--nbt FILE] [--metadata FILE] [--port 5189] [--open]

Reads a vanilla Java structure NBT and optional adjacent JSON metadata.
With no --nbt, opens maps/subway-station/subway-station.nbt if available.
Metadata may include name, creator, source_url, level_version, origin [x,y,z],
and entry [world eye x,y,z]. Map files are read only. The server binds to localhost.
`

export function parseArgs(argv) {
  const options = { nbt: path.join(root, 'maps/subway-station/subway-station.nbt'), port: 5189 }
  for (let i = 0; i < argv.length; i++) {
    const flag = argv[i]
    if (flag === '--open') options.open = true
    else if (flag === '--help' || flag === '-h') options.help = true
    else if (['--nbt', '--metadata', '--port'].includes(flag)) {
      if (!argv[i + 1] || argv[i + 1].startsWith('--')) throw Error(`${flag} requires a value`)
      options[flag.slice(2)] = argv[++i]
    } else throw Error(`Unknown argument: ${flag}`)
  }
  options.port = Number(options.port)
  if (!Number.isInteger(options.port) || options.port < 1 || options.port > 65535) throw Error('Port must be 1–65535')
  const callerCwd = process.env.INIT_CWD || process.cwd()
  options.metadataExplicit = options.metadata !== undefined
  options.nbt = path.resolve(callerCwd, options.nbt)
  options.metadata = path.resolve(callerCwd, options.metadata || path.join(path.dirname(options.nbt), path.basename(options.nbt, path.extname(options.nbt)) + '.json'))
  return options
}

export async function startPreview(options) {
  await fs.access(options.nbt).catch(() => { throw Error(`Structure not found: ${options.nbt}\nUse --nbt FILE. See map-previewer/README.md for world export.`) })
  let createServer
  try { ({ createServer } = await import('vite')) }
  catch { throw Error('Dependencies missing. Run: npm --prefix map-previewer ci') }
  const lodestoneRoot = path.dirname(path.dirname(fileURLToPath(import.meta.resolve('@mattzh72/lodestone'))))
  const pack = path.join(lodestoneRoot, 'assets/default-pack')
  let metadata = {}
  try { metadata = JSON.parse(await fs.readFile(options.metadata, 'utf8')) }
  catch (error) { if (error.code !== 'ENOENT' || options.metadataExplicit) throw Error(`Invalid metadata: ${error.message}`) }
  if (!metadata || Array.isArray(metadata) || typeof metadata !== 'object') throw Error('Metadata must be a JSON object')
  metadata.name ||= path.basename(options.nbt, path.extname(options.nbt))
  const server = await createServer({
    root: path.join(root, 'viewer'),
    server: { host: '127.0.0.1', port: options.port, strictPort: true, fs: { allow: [root] } },
    plugins: [{ name: 'map-preview-assets', configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = new URL(req.url, 'http://localhost')
        if (url.pathname === '/map.json') {
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(metadata))
          return
        }
        let file
        if (url.pathname === '/map.nbt') file = options.nbt
        else if (url.pathname.startsWith('/default-pack/')) {
          let relative
          try { relative = decodeURIComponent(url.pathname.slice('/default-pack/'.length)) }
          catch { res.statusCode = 400; res.end('Invalid path'); return }
          file = path.resolve(pack, relative)
          if (!file.startsWith(pack + path.sep)) { res.statusCode = 403; res.end('Forbidden'); return }
        } else { next(); return }
        const types = { '.nbt': 'application/octet-stream', '.png': 'image/png', '.json': 'application/json', '.txt': 'text/plain' }
        res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream')
        const stream = createReadStream(file)
        stream.on('error', () => { if (!res.headersSent) { res.statusCode = 404; res.end('Not found') } else res.destroy() })
        stream.pipe(res)
      })
    } }],
  })
  await server.listen()
  return server
}

async function main() {
  const options = parseArgs(process.argv.slice(2))
  if (options.help) { console.log(usage); return }
  const server = await startPreview(options)
  const url = `http://127.0.0.1:${options.port}/`
  console.log(`Map preview: ${url}`)
  if (options.open) {
    const opener = process.platform === 'darwin' ? 'open' : process.platform === 'win32' ? 'cmd' : 'xdg-open'
    const child = spawn(opener, process.platform === 'win32' ? ['/c', 'start', '', url] : [url], { detached: true, stdio: 'ignore' })
    child.on('error', error => console.warn(`Open ${url} in a browser (${error.message})`))
    child.unref()
  }
  for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, async () => { await server.close(); process.exit(0) })
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch(error => { console.error(`preview: ${error.message}`); process.exitCode = 1 })
}

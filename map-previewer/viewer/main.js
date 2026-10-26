import { loadDefaultPackResources } from '@mattzh72/lodestone'
import { PreviewRenderer } from './renderer.js'
import { boundsFromPoints, contains, fullBounds, measure, toWorld } from './selection.js'
import { readStructure } from './structure.js'
import './style.css'

const $ = id => document.getElementById(id)
const canvas = $('preview'), keys = new Set()
const add = (a, b, scale = 1) => a.map((value, axis) => value + b[axis] * scale)
const format = number => number.toLocaleString(undefined, { maximumFractionDigits: 1 })
let renderer, structure, blocks, metadata, size, origin, fallback, bounds
let points = [], pending = null, nextId = 1, tool = 'normal'
let cameraMode = 'orbit', center, distance, yaw = .8, pitch = .7
let eye, flyYaw = Math.PI, flyPitch = 0, speed = 10
let dirty = true, dragging = null, lastTime = 0, cutoff = Infinity
let rebuilding = false, rebuildRequested = false

function currentView() {
  if (cameraMode === 'fly') {
    const direction = [Math.sin(flyYaw) * Math.cos(flyPitch), Math.sin(flyPitch), -Math.cos(flyYaw) * Math.cos(flyPitch)]
    return { eye, target: add(eye, direction) }
  }
  return { eye: add(center, [Math.sin(yaw) * Math.cos(pitch), Math.sin(pitch), Math.cos(yaw) * Math.cos(pitch)], distance), target: center }
}

function setCameraMode(next) {
  if (next === 'fly' && cameraMode !== 'fly') {
    const state = currentView()
    eye = [...state.eye]
    const direction = state.target.map((value, axis) => value - eye[axis])
    flyYaw = Math.atan2(direction[0], -direction[2])
    flyPitch = Math.atan2(direction[1], Math.hypot(direction[0], direction[2]))
  } else if (next === 'orbit' && cameraMode === 'fly') {
    const state = currentView(), direction = state.target.map((value, axis) => value - eye[axis])
    distance = Math.max(15, Math.max(...size) / 8)
    center = add(eye, direction, distance)
    yaw = Math.atan2(-direction[0], -direction[2]); pitch = -flyPitch
  }
  cameraMode = next
  $('fly').textContent = `Fly: ${next === 'fly' ? 'on' : 'off'}`
  $('fly').setAttribute('aria-pressed', String(next === 'fly'))
  $('help').innerHTML = next === 'fly'
    ? 'Drag to look · WASD to fly · E/Q up/down.<br>Shift moves faster · scroll adjusts speed · F toggles orbit.'
    : 'Drag to orbit · right-drag to pan · scroll to zoom.<br>Choose Inside to fly through the build.'
  dirty = true
}

function overview() {
  setCameraMode('orbit')
  center = size.map(value => value / 2)
  distance = Math.max(15, Math.max(...size) * 1.15)
  yaw = .8; pitch = .7; dirty = true
}

function inside() {
  setCameraMode('fly')
  const entry = metadata.entry
  eye = Array.isArray(entry) && entry.length === 3 && entry.every(Number.isFinite)
    ? entry.map((value, axis) => value - origin[axis])
    : size.map(value => value / 2)
  flyYaw = Math.PI; flyPitch = .04; speed = 10; dirty = true
}

function newPoint(pos) { return { id: nextId++, pos: [...pos] } }

function wrapAll() {
  pending = null
  points = [newPoint(fallback.min), newPoint(fallback.max)]
  $('status').textContent = 'Box wraps the entire loaded structure.'
  updateSelection()
}

function setTool(next) {
  tool = next; pending = null
  for (const name of ['normal', 'extend']) $(name).setAttribute('aria-pressed', String(name === next))
  $('selection-help').textContent = next === 'normal'
    ? 'Click two blocks to set opposite corners. Drag to move the camera.'
    : 'Each click adds a point. Remove any point with × to recompute the box.'
  $('status').textContent = ''
  updateSelection()
}

function selectPoint(point) {
  if (tool === 'extend') {
    // An empty point list still wraps everything; preserve that extent when extending.
    if (!points.length) points = [newPoint(fallback.min), newPoint(fallback.max)]
    points.push(newPoint(point))
    $('status').textContent = `Added point ${points.length}. Remove × to undo its extent.`
  } else if (!pending) {
    pending = [...point]
    $('status').textContent = `First corner: ${toWorld(point, origin).join(', ')}. Select the opposite corner.`
  } else {
    points = [newPoint(pending), newPoint(point)]; pending = null
    $('status').textContent = 'Two corners selected. Extend adds more points; × removes a point.'
  }
  updateSelection()
}

function updateSelection() {
  bounds = boundsFromPoints(points.map(point => point.pos), fallback)
  const stats = measure(bounds)
  for (let axis = 0; axis < 3; axis++) $(`size-${'xyz'[axis]}`).textContent = `${format(stats.size[axis])} m`
  const count = blocks.reduce((total, block) => total + Number(contains(bounds, block.pos)), 0)
  $('measurement').textContent = `${format(stats.footprint)} m² footprint · ${format(stats.volume)} m³ box · ${format(count)} blocks inside`
  const min = toWorld(bounds.min, origin), max = toWorld(bounds.max, origin)
  $('bounds').textContent = `Min ${min.join(', ')}\nMax ${max.join(', ')}`
  $('bounds').style.whiteSpace = 'pre-line'
  $('dimensions').dataset.size = JSON.stringify(stats.size)
  $('dimensions').dataset.min = JSON.stringify(min)
  $('dimensions').dataset.max = JSON.stringify(max)
  $('points').replaceChildren(...points.map((point, index) => {
    const row = document.createElement('li'), label = document.createElement('span'), remove = document.createElement('button')
    label.textContent = `${index + 1}. ${toWorld(point.pos, origin).join(', ')}`
    remove.type = 'button'; remove.textContent = '×'; remove.dataset.id = point.id
    remove.setAttribute('aria-label', `Remove point ${index + 1}`)
    row.append(label, remove)
    return row
  }))
  renderer.drawMeasurement(bounds, pending)
  if ($('mask').checked) void rebuild()
  dirty = true
}

async function rebuild() {
  rebuildRequested = true
  if (rebuilding) return
  rebuilding = true
  document.documentElement.dataset.busy = 'true'
  try {
    while (rebuildRequested) {
      rebuildRequested = false
      const selected = { min: [...bounds.min], max: [...bounds.max] }
      const ceiling = cutoff, mask = $('mask').checked
      const visible = point => point[1] <= ceiling && (!mask || contains(selected, point))
      const kept = blocks.filter(block => visible(block.pos))
      renderer.setStructure({ getSize: () => size, getBlocks: () => kept, getBlock: point => visible(point) ? structure.getBlock(point) : null })
      await renderer.whenReady()
      document.documentElement.dataset.visibleBlocks = String(kept.length)
      dirty = true
    }
  } finally {
    rebuilding = false
    document.documentElement.dataset.busy = 'false'
  }
}

function selectAt(x, y) {
  const visible = point => point[1] <= cutoff && (!$('mask').checked || contains(bounds, point)) && structure.getBlock(point) !== null
  const hit = renderer.pick(x, y, size, visible)
  if (hit) selectPoint(hit)
  else $('status').textContent = 'No visible block at that point. Try a block surface or enter coordinates.'
}

function selectionData() {
  const stats = measure(bounds)
  return {
    name: metadata.name, source_url: metadata.source_url, units: 'blocks (1 block = 1 metre)',
    coordinates: 'world block cells, inclusive min and max', origin,
    points: points.map(point => toWorld(point.pos, origin)),
    min: toWorld(bounds.min, origin), max: toWorld(bounds.max, origin),
    size: stats.size, footprint: stats.footprint, volume: stats.volume, diagonal: stats.diagonal,
  }
}

canvas.addEventListener('contextmenu', event => event.preventDefault())
canvas.addEventListener('pointerdown', event => {
  dragging = { x: event.clientX, y: event.clientY, startX: event.clientX, startY: event.clientY,
    pan: event.button === 2 || event.shiftKey, button: event.button, moved: false }
  canvas.setPointerCapture(event.pointerId)
})
canvas.addEventListener('pointerup', event => {
  if (dragging && !dragging.moved && dragging.button === 0) selectAt(event.clientX, event.clientY)
  dragging = null
})
for (const event of ['pointercancel', 'lostpointercapture']) canvas.addEventListener(event, () => { dragging = null })
canvas.addEventListener('pointermove', event => {
  if (!dragging) return
  if (!dragging.moved) {
    if (Math.hypot(event.clientX - dragging.startX, event.clientY - dragging.startY) < 5) return
    dragging.moved = true
  }
  const dx = event.clientX - dragging.x, dy = event.clientY - dragging.y
  if (cameraMode === 'fly') {
    flyYaw += dx * .004; flyPitch = Math.max(-1.55, Math.min(1.55, flyPitch - dy * .004))
  } else if (dragging.pan) {
    const scale = distance * .0015
    center = add(center, [Math.cos(yaw), 0, -Math.sin(yaw)], -dx * scale)
    center = add(center, [-Math.sin(yaw) * Math.sin(pitch), Math.cos(pitch), -Math.cos(yaw) * Math.sin(pitch)], dy * scale)
  } else {
    yaw -= dx * .006; pitch = Math.max(-1.5, Math.min(1.5, pitch + dy * .006))
  }
  dragging.x = event.clientX; dragging.y = event.clientY; dirty = true
})
canvas.addEventListener('wheel', event => {
  event.preventDefault()
  if (cameraMode === 'fly') speed = Math.max(1, Math.min(180, speed * Math.exp(-event.deltaY * .002)))
  else distance = Math.max(1, Math.min(10000, distance * Math.exp(event.deltaY * .001)))
  dirty = true
}, { passive: false })
window.addEventListener('keydown', event => {
  if (event.target.closest('input, button, select, textarea')) return
  if (['KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyQ', 'KeyE', 'Space', 'ShiftLeft', 'ShiftRight'].includes(event.code)) {
    keys.add(event.code); event.preventDefault()
  }
  if (event.code === 'KeyF' && !event.repeat) setCameraMode(cameraMode === 'fly' ? 'orbit' : 'fly')
  if (event.code === 'Escape' && pending) { pending = null; $('status').textContent = 'Corner selection cancelled.'; updateSelection() }
})
window.addEventListener('keyup', event => keys.delete(event.code))
window.addEventListener('blur', () => keys.clear())
document.addEventListener('visibilitychange', () => { if (document.hidden) keys.clear() })
for (const [id, action] of Object.entries({ overview, inside, fly: () => setCameraMode(cameraMode === 'fly' ? 'orbit' : 'fly'),
  normal: () => setTool('normal'), extend: () => setTool('extend'), wrap: wrapAll })) {
  $(id).addEventListener('click', () => { action(); $(id).blur() })
}
$('points').addEventListener('click', event => {
  const button = event.target.closest('button[data-id]')
  if (!button) return
  points = points.filter(point => point.id !== Number(button.dataset.id)); pending = null
  $('status').textContent = points.length ? 'Box recomputed from the remaining points.' : 'No points left; box wraps the entire structure.'
  updateSelection()
})
$('point-form').addEventListener('submit', event => {
  event.preventDefault()
  const point = ['x', 'y', 'z'].map(axis => Number($(`point-${axis}`).value))
  if (!point.every(Number.isSafeInteger)) { $('status').textContent = 'Enter integer block coordinates.'; return }
  selectPoint(point.map((value, axis) => value - origin[axis]))
})
$('mask').addEventListener('change', () => { void rebuild() })
$('height').addEventListener('input', event => { $('height-label').textContent = event.target.value === event.target.max ? 'full' : `Y ${event.target.value}` })
$('height').addEventListener('change', event => { cutoff = Number(event.target.value) - origin[1]; void rebuild() })
$('copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(JSON.stringify(selectionData(), null, 2)); $('status').textContent = 'Bounds copied in world coordinates.' }
  catch { $('status').textContent = 'Clipboard unavailable; use Export selection to save the coordinates.' }
})
$('export').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(selectionData(), null, 2) + '\n'], { type: 'application/json' }))
  const link = document.createElement('a')
  link.href = url; link.download = `${metadata.name.replace(/[^a-z0-9_-]/gi, '-')}.selection.json`; link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
})

function placeLabels() {
  const extent = measure(bounds).size
  for (let axis = 0; axis < 3; axis++) {
    const point = [...bounds.min]
    point[axis] += extent[axis] / 2
    const projected = renderer.project(point), label = $(`axis-${'xyz'[axis]}`)
    label.textContent = `${'XYZ'[axis]} ${format(extent[axis])} m`
    const [x, y, z] = projected
    label.style.display = z >= -1 && z <= 1 && Math.abs(x) <= 1 && Math.abs(y) <= 1 ? 'block' : 'none'
    label.style.left = `${(x + 1) * innerWidth / 2}px`
    label.style.top = `${(1 - y) * innerHeight / 2}px`
  }
}

function frame(time) {
  const dt = Math.min((time - lastTime) / 1000, .1); lastTime = time
  if (cameraMode === 'fly' && keys.size) {
    const forward = [Math.sin(flyYaw) * Math.cos(flyPitch), Math.sin(flyPitch), -Math.cos(flyYaw) * Math.cos(flyPitch)]
    const right = [Math.cos(flyYaw), 0, Math.sin(flyYaw)]
    let delta = [0, 0, 0]
    if (keys.has('KeyW')) delta = add(delta, forward)
    if (keys.has('KeyS')) delta = add(delta, forward, -1)
    if (keys.has('KeyD')) delta = add(delta, right)
    if (keys.has('KeyA')) delta = add(delta, right, -1)
    if (keys.has('KeyE') || keys.has('Space')) delta[1] += 1
    if (keys.has('KeyQ')) delta[1] -= 1
    const length = Math.hypot(...delta)
    if (length) {
      eye = add(eye, delta, speed * dt * (keys.has('ShiftLeft') || keys.has('ShiftRight') ? 4 : 1) / length)
      dirty = true
    }
  }
  if (dirty && renderer) {
    const state = currentView()
    renderer.inspectionDistance(cameraMode === 'fly' ? 80 : Math.max(2000, distance * 2))
    renderer.lookAt(state.eye, state.target)
    renderer.drawStructure()
    $('coords').textContent = `World XYZ ${toWorld(state.eye, origin).map(Math.round).join(' / ')}${cameraMode === 'fly' ? ` · ${Math.round(speed)} blocks/s` : ''}`
    placeLabels(); dirty = false
    document.documentElement.dataset.frame = String(time)
  }
  requestAnimationFrame(frame)
}

async function main() {
  const [bytes, info, pack] = await Promise.all([
    fetch('/map.nbt').then(response => { if (!response.ok) throw Error('Map could not be loaded'); return response.arrayBuffer() }),
    fetch('/map.json').then(response => response.json()),
    loadDefaultPackResources({ baseUrl: new URL('/default-pack/', location.href).href }),
  ])
  metadata = info
  origin = Array.isArray(info.origin) && info.origin.length === 3 && info.origin.every(Number.isFinite) ? info.origin : [0, 0, 0]
  ;({ structure, size, blocks } = readStructure(new Uint8Array(bytes)))
  fallback = fullBounds(size); cutoff = size[1] - 1
  center = size.map(value => value / 2); eye = [...center]; distance = Math.max(15, Math.max(...size) * 1.15)
  $('name').textContent = metadata.name; document.title = `${metadata.name} · Map preview`
  if (metadata.creator) {
    const credit = document.createElement('a')
    credit.textContent = metadata.creator
    if (/^https?:\/\//.test(metadata.source_url)) { credit.href = metadata.source_url; credit.target = '_blank'; credit.rel = 'noopener noreferrer' }
    $('source').append('By ', credit)
  }
  if (metadata.level_version) $('source').append(`${metadata.creator ? ' · ' : ''}Java ${metadata.level_version}`)
  $('stats').textContent = `${size.join(' × ')} blocks · ${format(blocks.length)} visible blocks`
  for (let axis = 0; axis < 3; axis++) $(`point-${'xyz'[axis]}`).value = origin[axis]
  $('height').min = origin[1]; $('height').max = origin[1] + size[1] - 1; $('height').value = $('height').max
  renderer = new PreviewRenderer(canvas, structure, pack.resources, {
    chunkSize: 16, drawDistance: 2000, asyncBuild: true, asyncChunkBuildTimeMs: 8, antialias: false,
    sunlight: { direction: [.35, .85, .25], intensity: .85, ambientIntensity: .95, fillIntensity: .45, rimIntensity: .15,
      exposure: 1.08, shadow: { enabled: false }, fog: { density: 0 },
      sky: { zenithColor: [.24, .48, .84], horizonColor: [.78, .9, 1], groundColor: [.18, .2, .22], stars: { enabled: false } },
    },
  })
  const gl = canvas.getContext('webgl2'), gpuInfo = gl?.getExtension('WEBGL_debug_renderer_info')
  const gpu = gpuInfo ? gl.getParameter(gpuInfo.UNMASKED_RENDERER_WEBGL) : ''
  const resolution = /swiftshader|llvmpipe|software/i.test(gpu) ? .5 : .75
  const resize = () => { renderer.setViewport(0, 0, innerWidth, innerHeight, resolution); dirty = true }
  window.addEventListener('resize', resize); resize()
  await renderer.whenReady()
  wrapAll()
  $('loading').classList.add('hidden')
  if (['inside', 'platform'].includes(new URLSearchParams(location.search).get('view'))) inside()
  document.documentElement.dataset.ready = 'true'
  requestAnimationFrame(frame)
}

main().catch(error => { console.error(error); $('loading').textContent = error.message })

import { ThreeStructureRenderer } from '@mattzh72/lodestone'
import { BoxGeometry, EdgesGeometry, LineBasicMaterial, LineSegments, Raycaster, Vector2, Vector3 } from 'three'
import { pickVoxel } from './selection.js'

// These hooks use Lodestone 0.6.0 internals. Keep the dependency pinned and check
// picking, lighting, overlays, and clipping together when upgrading Lodestone.
export class PreviewRenderer extends ThreeStructureRenderer {
  updateEmissiveLightsForCamera() {
    if (this.emissiveSelectionDirty || this.lastEmissiveLightCount !== 0) {
      this.updateEmissiveLightUniforms([])
      this.lastEmissiveLightCount = 0
      this.emissiveSelectionDirty = false
    }
  }

  inspectionDistance(distance) { this.drawDistance = distance }

  drawMeasurement(bounds, pending) {
    for (const object of this.measurementObjects || []) {
      this.overlayScene.remove(object)
      object.geometry.dispose()
      object.material.dispose()
    }
    this.measurementObjects = []
    const box = (min, max, color) => {
      const size = max.map((value, axis) => value - min[axis] + 1)
      const solid = new BoxGeometry(...size)
      const geometry = new EdgesGeometry(solid)
      solid.dispose()
      const line = new LineSegments(geometry, new LineBasicMaterial({ color, depthTest: false, depthWrite: false, transparent: true, opacity: .9 }))
      line.position.set(...min.map((value, axis) => value + size[axis] / 2))
      line.renderOrder = 20
      this.overlayScene.add(line)
      this.measurementObjects.push(line)
    }
    box(bounds.min, bounds.max, 0x70e4be)
    if (pending) box(pending, pending, 0xffcb6b)
  }

  pick(clientX, clientY, size, occupied) {
    const rect = this.renderer.domElement.getBoundingClientRect()
    const cursor = new Vector2((clientX - rect.left) / rect.width * 2 - 1, -(clientY - rect.top) / rect.height * 2 + 1)
    const raycaster = new Raycaster()
    this.camera.updateMatrixWorld()
    raycaster.setFromCamera(cursor, this.camera)
    return pickVoxel(raycaster.ray.origin.toArray(), raycaster.ray.direction.toArray(), size, occupied)
  }

  project(point) {
    return new Vector3(...point).project(this.camera).toArray()
  }
}

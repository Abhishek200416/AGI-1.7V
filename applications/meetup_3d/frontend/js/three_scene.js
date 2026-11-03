/**
 * NexusMeet 3D — Three.js Spatial Scene Engine & Scroll Rigging.
 * Renders 3D glowing meetup nodes, particle starfield, and smooth camera interpolation.
 */

class SpatialSceneManager {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.particles = null;
    this.meetupNodes = [];
    this.targetCameraPos = new THREE.Vector3(0, 0, 5);
    this.targetLookAt = new THREE.Vector3(0, 0, 0);
    this.currentLookAt = new THREE.Vector3(0, 0, 0);
    this.mouse = { x: 0, y: 0 };
    this.scrollProgress = 0;
    this.waypoints = [
      { cam: new THREE.Vector3(0, 0, 5), look: new THREE.Vector3(0, 0, 0) }, // Hero
    ];
    this.init();
  }

  init() {
    // 1. Scene & Camera
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x06080d, 0.045);

    const aspect = window.innerWidth / window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
    this.camera.position.set(0, 0, 5);

    // 2. WebGL Renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00f0ff, 1.2);
    dirLight.position.set(5, 10, 7);
    this.scene.add(dirLight);

    // 4. Particle Starfield
    this.createStarfield();

    // 5. Event Listeners
    window.addEventListener('resize', () => this.onWindowResize());
    window.addEventListener('mousemove', (e) => this.onMouseMove(e));
    window.addEventListener('scroll', () => this.onScroll());

    // 6. Animation Loop
    this.animate();
  }

  createStarfield() {
    const count = 1800;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const c1 = new THREE.Color(0x00f0ff);
    const c2 = new THREE.Color(0xa855f7);

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 50;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 50;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 40 - 10;

      const mixed = Math.random() > 0.5 ? c1 : c2;
      colors[i * 3] = mixed.r;
      colors[i * 3 + 1] = mixed.g;
      colors[i * 3 + 2] = mixed.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.12,
      vertexColors: true,
      transparent: true,
      opacity: 0.75,
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  addMeetupNodes(events) {
    // Clear previous
    this.meetupNodes.forEach(n => this.scene.remove(n.group));
    this.meetupNodes = [];
    this.waypoints = [{ cam: new THREE.Vector3(0, 0, 5), look: new THREE.Vector3(0, 0, 0) }];

    const geometries = [
      new THREE.IcosahedronGeometry(0.85, 0),
      new THREE.TorusGeometry(0.7, 0.25, 16, 32),
      new THREE.OctahedronGeometry(0.9, 0),
      new THREE.DodecahedronGeometry(0.85, 0),
    ];

    events.forEach((evt, idx) => {
      const group = new THREE.Group();
      const coords = evt.coordinates_3d || { x: 0, y: 0, z: 0 };
      group.position.set(coords.x, coords.y, coords.z);

      const colorHex = parseInt(evt.glow_color.replace('#', '0x'), 16) || 0x00f0ff;

      // Inner Core Mesh
      const geom = geometries[idx % geometries.length];
      const mat = new THREE.MeshStandardMaterial({
        color: colorHex,
        emissive: colorHex,
        emissiveIntensity: 0.45,
        roughness: 0.2,
        metalness: 0.8,
        wireframe: false,
      });
      const core = new THREE.Mesh(geom, mat);
      group.add(core);

      // Outer Wireframe Orbital Ring
      const ringGeom = new THREE.RingGeometry(1.2, 1.25, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: colorHex,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5,
      });
      const ring = new THREE.Mesh(ringGeom, ringMat);
      ring.rotation.x = Math.PI / 2;
      group.add(ring);

      // Point Light
      const pLight = new THREE.PointLight(colorHex, 2.5, 8);
      group.add(pLight);

      this.scene.add(group);
      this.meetupNodes.push({ group, core, ring, event: evt });

      // Add Waypoint for Camera
      // Camera looks directly at node, positioned slightly offset for card readability
      const camOffset = coords.x < 0 ? new THREE.Vector3(1.8, 0.4, 3.2) : new THREE.Vector3(-1.8, 0.4, 3.2);
      const camPos = new THREE.Vector3(coords.x + camOffset.x, coords.y + camOffset.y, coords.z + camOffset.z);
      this.waypoints.push({ cam: camPos, look: new THREE.Vector3(coords.x, coords.y, coords.z) });
    });

    // Add footer waypoint
    this.waypoints.push({
      cam: new THREE.Vector3(0, -9.0, -18.0),
      look: new THREE.Vector3(0, -9.0, -22.0),
    });
  }

  onScroll() {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    this.scrollProgress = maxScroll > 0 ? window.scrollY / maxScroll : 0;

    // Map scrollProgress [0..1] across waypoints
    const totalSegments = Math.max(1, this.waypoints.length - 1);
    const progressSegment = this.scrollProgress * totalSegments;
    const currentIdx = Math.min(totalSegments - 1, Math.floor(progressSegment));
    const nextIdx = Math.min(totalSegments, currentIdx + 1);
    const factor = progressSegment - currentIdx;

    const wpA = this.waypoints[currentIdx];
    const wpB = this.waypoints[nextIdx];

    if (wpA && wpB) {
      this.targetCameraPos.lerpVectors(wpA.cam, wpB.cam, factor);
      this.targetLookAt.lerpVectors(wpA.look, wpB.look, factor);
    }
  }

  onMouseMove(e) {
    this.mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    this.mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  }

  onWindowResize() {
    if (!this.camera || !this.renderer) return;
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    // 1. Smooth Camera Movement
    this.camera.position.lerp(this.targetCameraPos, 0.05);
    // Add subtle mouse parallax
    this.camera.position.x += (this.mouse.x * 0.4 - this.camera.position.x + this.targetCameraPos.x) * 0.02;
    this.camera.position.y += (this.mouse.y * 0.3 - this.camera.position.y + this.targetCameraPos.y) * 0.02;

    this.currentLookAt.lerp(this.targetLookAt, 0.06);
    this.camera.lookAt(this.currentLookAt);

    // 2. Rotate Meetup Nodes
    this.meetupNodes.forEach((node, i) => {
      node.core.rotation.x += 0.008 * (i % 2 === 0 ? 1 : -1);
      node.core.rotation.y += 0.012;
      node.ring.rotation.z += 0.005;
    });

    // 3. Rotate Starfield
    if (this.particles) {
      this.particles.rotation.y += 0.0003;
      this.particles.rotation.x += 0.0001;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

// Global scene manager instance
window.spatialScene = null;
document.addEventListener('DOMContentLoaded', () => {
  window.spatialScene = new SpatialSceneManager('webgl-canvas');
});

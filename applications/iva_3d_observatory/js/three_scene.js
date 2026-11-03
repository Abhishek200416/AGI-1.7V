/**
 * Three.js 3D Neural Observatory & Interactive Quantum Simulation Scene
 * Autonomous 3D Visualization Engine for IVA AGI 1.7.
 */

(function () {
    let scene, camera, renderer, controls;
    let coreMesh, particlesMesh, nodesGroup, linesGroup;
    let neuralNodes = [];
    let raycaster, mouse;
    let hoveredNode = null;
    let autoRotate = true;
    let particleSpeed = 1.0;
    let pulseFrequency = 1.2;
    let isWireframe = false;

    // Performance tracking
    let lastTime = performance.now();
    let frameCount = 0;
    let fps = 60;

    const container = document.getElementById('canvas-container');
    const fpsElem = document.getElementById('fps-counter');
    const raycastPosElem = document.getElementById('raycast-pos');
    const inspectorContent = document.getElementById('inspector-content');

    function init() {
        // 1. Scene & Camera Setup
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x07090e, 0.008);

        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 18, 55);

        // 2. Renderer
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        container.appendChild(renderer.domElement);

        // 3. Orbit Controls
        if (typeof THREE.OrbitControls !== 'undefined') {
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxDistance = 120;
            controls.minDistance = 10;
        }

        // 4. Lighting
        const ambientLight = new THREE.AmbientLight(0x1a2634, 1.5);
        scene.add(ambientLight);

        const pointLightCyan = new THREE.PointLight(0x00f3ff, 2, 80);
        pointLightCyan.position.set(20, 20, 20);
        scene.add(pointLightCyan);

        const pointLightMagenta = new THREE.PointLight(0xff007f, 2, 80);
        pointLightMagenta.position.set(-20, -15, -20);
        scene.add(pointLightMagenta);

        // 5. Build 3D Entities
        createCoreIcosahedron();
        createQuantumParticles();
        createNeuralCluster(64);
        createSynapticConnections();

        // 6. Raycasting Setup
        raycaster = new THREE.Raycaster();
        mouse = new THREE.Vector2(-999, -999);

        // Event Listeners
        window.addEventListener('resize', onWindowResize);
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('click', onMouseClick);

        setupControlsUI();

        // Start Render Loop
        animate();
    }

    function createCoreIcosahedron() {
        const geometry = new THREE.IcosahedronGeometry(7, 3);
        const material = new THREE.MeshStandardMaterial({
            color: 0x05101a,
            emissive: 0x00f3ff,
            emissiveIntensity: 0.35,
            roughness: 0.2,
            metalness: 0.85,
            wireframe: false
        });
        coreMesh = new THREE.Mesh(geometry, material);
        scene.add(coreMesh);

        // Outer wireframe shell
        const wireMaterial = new THREE.MeshBasicMaterial({
            color: 0x00f3ff,
            wireframe: true,
            transparent: true,
            opacity: 0.25
        });
        const shell = new THREE.Mesh(new THREE.IcosahedronGeometry(8, 2), wireMaterial);
        coreMesh.add(shell);
    }

    function createQuantumParticles() {
        const count = 2500;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        const colors = new Float32Array(count * 3);

        const color1 = new THREE.Color(0x00f3ff);
        const color2 = new THREE.Color(0xa855f7);

        for (let i = 0; i < count; i++) {
            const radius = 22 + Math.random() * 28;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);

            positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = (radius * Math.sin(phi) * Math.sin(theta)) * 0.45;
            positions[i * 3 + 2] = radius * Math.cos(phi);

            const mixed = color1.clone().lerp(color2, Math.random());
            colors[i * 3] = mixed.r;
            colors[i * 3 + 1] = mixed.g;
            colors[i * 3 + 2] = mixed.b;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 0.7,
            vertexColors: true,
            transparent: true,
            opacity: 0.75,
            blending: THREE.AdditiveBlending
        });

        particlesMesh = new THREE.Points(geometry, material);
        scene.add(particlesMesh);
    }

    function createNeuralCluster(numNodes) {
        nodesGroup = new THREE.Group();
        neuralNodes = [];

        const domains = [
            { name: "FRONTEND_UIUX", color: 0x00f3ff, freq: 520 },
            { name: "CYBER_SECURITY", color: 0xff0055, freq: 660 },
            { name: "CODE_INTELLIGENCE", color: 0x10b981, freq: 740 },
            { name: "BROWSER_AUTOMATION", color: 0xa855f7, freq: 880 },
            { name: "DATA_ANALYTICS", color: 0xf59e0b, freq: 960 },
            { name: "COGNITIVE_REASONING", color: 0x38bdf8, freq: 1100 }
        ];

        for (let i = 0; i < numNodes; i++) {
            const domain = domains[i % domains.length];
            const radius = 15 + Math.random() * 12;
            const phi = Math.acos(-1 + (2 * i) / numNodes);
            const theta = Math.sqrt(numNodes * Math.PI) * phi;

            const x = radius * Math.cos(theta) * Math.sin(phi);
            const y = radius * Math.sin(theta) * Math.sin(phi);
            const z = radius * Math.cos(phi);

            const sphereGeo = new THREE.SphereGeometry(0.85, 16, 16);
            const sphereMat = new THREE.MeshStandardMaterial({
                color: domain.color,
                emissive: domain.color,
                emissiveIntensity: 0.4,
                roughness: 0.3,
                metalness: 0.7
            });

            const nodeMesh = new THREE.Mesh(sphereGeo, sphereMat);
            nodeMesh.position.set(x, y, z);
            nodeMesh.userData = {
                id: `NODE-0x${(i + 1).toString(16).padStart(3, '0').toUpperCase()}`,
                domain: domain.name,
                clusterIndex: i,
                baseFrequency: domain.freq,
                synapticWeight: (0.7 + Math.random() * 0.29).toFixed(4),
                memoryPointer: `0x7FFF_${(Math.random() * 0xFFFFFF << 0).toString(16).toUpperCase()}`
            };

            nodesGroup.add(nodeMesh);
            neuralNodes.push(nodeMesh);
        }

        scene.add(nodesGroup);
    }

    function createSynapticConnections() {
        linesGroup = new THREE.Group();
        const lineMaterial = new THREE.LineBasicMaterial({
            color: 0x00f3ff,
            transparent: true,
            opacity: 0.18,
            blending: THREE.AdditiveBlending
        });

        for (let i = 0; i < neuralNodes.length; i++) {
            for (let j = i + 1; j < neuralNodes.length; j++) {
                const dist = neuralNodes[i].position.distanceTo(neuralNodes[j].position);
                if (dist < 11) {
                    const points = [neuralNodes[i].position, neuralNodes[j].position];
                    const geometry = new THREE.BufferGeometry().setFromPoints(points);
                    const line = new THREE.Line(geometry, lineMaterial);
                    linesGroup.add(line);
                }
            }
        }
        scene.add(linesGroup);
    }

    function onMouseMove(event) {
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    function onMouseClick(event) {
        if (!hoveredNode) return;
        window.neuralAudio.init();
        window.neuralAudio.playNodeSelect(hoveredNode.userData.baseFrequency);
        displayNodeDetails(hoveredNode.userData);
    }

    function displayNodeDetails(data) {
        inspectorContent.innerHTML = `
            <div class="node-card">
                <h5>${data.id} • ${data.domain}</h5>
                <div class="node-stat-row">
                    <span class="dim-text">Memory Pointer:</span>
                    <strong class="highlight-cyan">${data.memoryPointer}</strong>
                </div>
                <div class="node-stat-row">
                    <span class="dim-text">Synaptic Weight:</span>
                    <strong class="highlight-purple">${data.synapticWeight}</strong>
                </div>
                <div class="node-stat-row">
                    <span class="dim-text">Resonant Freq:</span>
                    <strong class="highlight-green">${data.baseFrequency} Hz</strong>
                </div>
                <div class="node-stat-row">
                    <span class="dim-text">Status:</span>
                    <strong class="highlight-gold">ACTIVE IN 1M+ CONTEXT</strong>
                </div>
            </div>
        `;
    }

    function setupControlsUI() {
        const speedInput = document.getElementById('particle-speed');
        if (speedInput) {
            speedInput.addEventListener('input', (e) => {
                particleSpeed = parseFloat(e.target.value);
            });
        }

        const pulseInput = document.getElementById('pulse-freq');
        if (pulseInput) {
            pulseInput.addEventListener('input', (e) => {
                pulseFrequency = parseFloat(e.target.value);
            });
        }

        const wireBtn = document.getElementById('wireframe-btn');
        if (wireBtn) {
            wireBtn.addEventListener('click', () => {
                isWireframe = !isWireframe;
                coreMesh.material.wireframe = isWireframe;
                neuralNodes.forEach(n => n.material.wireframe = isWireframe);
                wireBtn.classList.toggle('active', isWireframe);
            });
        }

        const rotateBtn = document.getElementById('rotate-btn');
        if (rotateBtn) {
            rotateBtn.addEventListener('click', () => {
                autoRotate = !autoRotate;
                rotateBtn.textContent = `AUTO-ROTATE: ${autoRotate ? 'ON' : 'OFF'}`;
                rotateBtn.classList.toggle('active', autoRotate);
            });
        }

        const audioBtn = document.getElementById('audio-toggle-btn');
        if (audioBtn) {
            audioBtn.addEventListener('click', () => {
                const active = window.neuralAudio.toggle();
                audioBtn.textContent = `🔊 AUDIO: ${active ? 'ON' : 'OFF'}`;
                audioBtn.classList.toggle('active', active);
            });
        }
    }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function animate() {
        requestAnimationFrame(animate);

        const time = performance.now() * 0.001;

        // FPS calculation
        frameCount++;
        if (performance.now() - lastTime >= 1000) {
            fps = frameCount;
            frameCount = 0;
            lastTime = performance.now();
            if (fpsElem) fpsElem.textContent = fps;
        }

        // Auto-rotation & pulsing animation
        if (autoRotate) {
            coreMesh.rotation.y += 0.006 * pulseFrequency;
            coreMesh.rotation.x += 0.003 * pulseFrequency;
            particlesMesh.rotation.y -= 0.002 * particleSpeed;
            nodesGroup.rotation.y += 0.003 * pulseFrequency;
            linesGroup.rotation.y += 0.003 * pulseFrequency;
        }

        // Core pulsing breathing effect
        const scale = 1 + 0.06 * Math.sin(time * 2.5 * pulseFrequency);
        coreMesh.scale.set(scale, scale, scale);

        // Raycasting node hover
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(neuralNodes);

        if (intersects.length > 0) {
            const hit = intersects[0].object;
            if (hoveredNode !== hit) {
                if (hoveredNode) hoveredNode.scale.set(1, 1, 1);
                hoveredNode = hit;
                hoveredNode.scale.set(1.4, 1.4, 1.4);
                window.neuralAudio.init();
                window.neuralAudio.playNodeHover(hoveredNode.userData.baseFrequency);
                if (raycastPosElem) {
                    raycastPosElem.textContent = `${hoveredNode.userData.id} [${hoveredNode.position.x.toFixed(1)}, ${hoveredNode.position.y.toFixed(1)}, ${hoveredNode.position.z.toFixed(1)}]`;
                }
            }
        } else {
            if (hoveredNode) {
                hoveredNode.scale.set(1, 1, 1);
                hoveredNode = null;
                if (raycastPosElem) raycastPosElem.textContent = "Orbiting Core (0, 0, 0)";
            }
        }

        if (controls) controls.update();
        renderer.render(scene, camera);
    }

    window.addEventListener('DOMContentLoaded', init);
})();

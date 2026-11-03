/**
 * AETHERIA 3D • Universal Scale Journey (240 FPS Ultra-Smooth Engine)
 * =============================================================================
 * Hierarchical Procedural Universe:
 * Scale 1: Planet (Earth & Moon, Saturn Rings, Jupiter)
 * Scale 2: Solar System (Sun + 8 Orbiting Worlds + Asteroid/Kuiper Belts)
 * Scale 3: Milky Way Galaxy (35,000 Spiral Arm Stars & Sagittarius A* Core)
 * Scale 4: Laniakea Galactic Supercluster (Swirling Galaxies in Cosmic Ocean)
 * Scale 5: Observable Cosmic Web (Dark Matter Neural Filaments)
 *
 * Ultra-Smooth 240 FPS: Delta-time normalized physics & frame-independent lerp.
 * Zen Mode Fix: Dedicated floating restore eye button for seamless recovery.
 * =============================================================================
 */

(function () {
    let scene, camera, renderer, controls, clock;
    let coreGroup, particleSystem, solarSystemGroup, superclusterGroup, cosmicWebGroup;
    let planetaryBodies = [];
    let anomalies = [];
    let selectedTarget = null;

    // Simulation tuning
    let particlesCount = 35000;
    let particlePositions, particleVelocities, particleColors, particleGeometry;
    let raycaster, mouse;
    let activeTheme = "violet";
    let speedMult = 1.0;
    let gravityMult = 1.0;
    let isWarping = false;
    let warpFactor = 1.0;

    // Device detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;

    // Scale Tier Architecture (1: Planet -> 5: Cosmic Web)
    let currentScale = "solar_system";
    let scaleData = {
        planetary: { dist: 24, fov: 50, badge: "🌍 Terrestrial (10^7 m)", chronicle: "A sapphire jewel, cradled in stellar grace, where life's delicate whispers find their place." },
        solar_system: { dist: 140, fov: 60, badge: "☀️ Heliosphere (10^13 m)", chronicle: "A dance of worlds around a fiery heart, a miniature cosmos, a celestial art." },
        milky_way: { dist: 650, fov: 65, badge: "🌌 Milky Way (10^21 m)", chronicle: "A spiral arm of starlight, vast and deep, where billions of suns their ancient vigil keep." },
        supercluster: { dist: 1800, fov: 70, badge: "🌀 Laniakea Supercluster (10^24 m)", chronicle: "Clusters gathered, a cosmic congregation grand, a tapestry woven across the stellar land." },
        cosmic_web: { dist: 4200, fov: 75, badge: "🕸️ Observable Cosmic Web (10^26 m)", chronicle: "Filaments of matter, a web of infinite might, shaping the universe in eternal, cosmic light." }
    };

    // Camera target for delta-time smooth tweening
    let targetCameraPos = null;
    let targetLookAt = new THREE.Vector3(0, 0, 0);
    let currentLookAt = new THREE.Vector3(0, 0, 0);

    // Cinematic Ingress Hook
    let isIngress = true;
    let ingressStart = performance.now();
    let ingressDuration = 2400;
    const startPos = new THREE.Vector3(0, 110, 240);
    const targetOrbitPos = new THREE.Vector3(0, isMobile ? 36 : 30, isMobile ? 96 : 85);

    // Zen Mode & Idle Auto-Hide
    let idleTimer = null;
    let isZenMode = false;

    // True High-Refresh 240 FPS Telemetry
    let lastFpsTime = performance.now();
    let frameCount = 0;
    let currentFps = 60;

    const container = document.getElementById("canvas-container");
    const capsuleFps = document.getElementById("capsule-fps");
    const microParticles = document.getElementById("micro-particles");
    const microScale = document.getElementById("micro-scale");
    const microFps = document.getElementById("micro-fps");
    const introHookChip = document.getElementById("intro-hook-chip");
    const dismissHookBtn = document.getElementById("dismiss-hook-btn");
    const zenExitBtn = document.getElementById("zen-exit-floating-btn");

    // Scale Chronicle Card
    const scaleChronicleCard = document.getElementById("scale-chronicle-card");
    const scaleBadgeText = document.getElementById("scale-badge-text");
    const scaleChronicleText = document.getElementById("scale-chronicle-text");
    const closeChronicleBtn = document.getElementById("close-chronicle-btn");

    // Modals
    const tuningDeck = document.getElementById("tuning-deck");
    const anomaliesSheet = document.getElementById("anomalies-sheet");
    const inspector = document.getElementById("right-inspector");
    const anomaliesList = document.getElementById("anomalies-list");

    const inspectorTitle = document.getElementById("inspector-title");
    const inspectorSector = document.getElementById("inspector-sector");
    const inspectorFreq = document.getElementById("inspector-freq");
    const inspectorLore = document.getElementById("inspector-lore");
    const inspectorEnergy = document.getElementById("inspector-energy");
    const oracleOutput = document.getElementById("oracle-output");

    // Chromatic Palettes
    const PALETTES = {
        violet: {
            core: 0xffa200,
            ring: 0x00f3ff,
            dust1: new THREE.Color(0x9d4edd),
            dust2: new THREE.Color(0x00f3ff),
            dust3: new THREE.Color(0xff007f),
            fog: 0x030408
        },
        aurora: {
            core: 0x38ef7d,
            ring: 0x00f3ff,
            dust1: new THREE.Color(0x38ef7d),
            dust2: new THREE.Color(0x11998e),
            dust3: new THREE.Color(0x00f3ff),
            fog: 0x020706
        },
        solar: {
            core: 0xff8c00,
            ring: 0xff3838,
            dust1: new THREE.Color(0xffd166),
            dust2: new THREE.Color(0xff5e36),
            dust3: new THREE.Color(0xffffff),
            fog: 0x080402
        },
        void: {
            core: 0x718096,
            ring: 0x4a5568,
            dust1: new THREE.Color(0xa0aec0),
            dust2: new THREE.Color(0x4a5568),
            dust3: new THREE.Color(0x2d3748),
            fog: 0x020204
        }
    };

    function init() {
        clock = new THREE.Clock();

        if (isMobile) {
            particlesCount = 18000;
        }

        // 1. Scene & Depth Fog
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(PALETTES.violet.fog, 0.00045);

        // 2. Camera: Wide dynamic range for planetary to cosmic web scaling (0.1 to 15,000 units)
        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 15000);
        camera.position.copy(startPos);

        // 3. 240 FPS High-Performance WebGL Renderer
        renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: "high-performance",
            precision: "highp",
            preserveDrawingBuffer: true
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.3;
        container.appendChild(renderer.domElement);

        // 4. Orbit Controls (Configured for 240 FPS smooth touch gestures)
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = 8000;
        controls.minDistance = 6;
        controls.touches = {
            ONE: THREE.TOUCH.ROTATE,
            TWO: THREE.TOUCH.DOLLY_PAN
        };

        // 5. Ambient & Directional Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
        scene.add(ambientLight);

        const centralSunLight = new THREE.PointLight(0xffffff, 3.5, 300);
        centralSunLight.position.set(0, 0, 0);
        scene.add(centralSunLight);

        // 6. Raycasting
        raycaster = new THREE.Raycaster();
        raycaster.params.Points.threshold = 1.5;
        mouse = new THREE.Vector2(-999, -999);

        // 7. Build All 5 Cosmic Scale Systems
        createSolarSystemScale();
        createMilkyWayGalaxy(particlesCount);
        createSuperclusterScale();
        createCosmicWebScale();
        createCelestialAnomalies();

        // 8. Event Listeners
        window.addEventListener("resize", onWindowResize);
        window.addEventListener("mousemove", onUserActive);
        window.addEventListener("touchstart", onUserActive, { passive: true });
        window.addEventListener("click", onCanvasClick);

        setupTouchInteraction();
        setupScaleRibbon();
        setupErgonomicControls();

        ingressStart = performance.now();
        animate(performance.now());
    }

    /**
     * Scale 1 & 2: Solar System Architecture (Sun + 8 Orbiting Planets + Rings + Asteroid Belt)
     */
    function createSolarSystemScale() {
        solarSystemGroup = new THREE.Group();

        // 1. Central Sun
        const sunGeo = new THREE.IcosahedronGeometry(5.5, 3);
        const sunMat = new THREE.MeshBasicMaterial({
            color: 0xffa200,
            wireframe: true,
            transparent: true,
            opacity: 0.95
        });
        const sunMesh = new THREE.Mesh(sunGeo, sunMat);
        solarSystemGroup.add(sunMesh);

        // Solar Coronal Glow Halo
        const sunHaloGeo = new THREE.SphereGeometry(7.0, 24, 24);
        const sunHaloMat = new THREE.MeshBasicMaterial({
            color: 0xffd166,
            wireframe: true,
            transparent: true,
            opacity: 0.35
        });
        const sunHalo = new THREE.Mesh(sunHaloGeo, sunHaloMat);
        solarSystemGroup.add(sunHalo);

        // 2. Planets Data
        const planetConfigs = [
            { name: "Mercury", radius: 0.55, dist: 12, speed: 0.038, color: 0xa8a8a8, lore: "Sun-scorched iron world in rapid tidal resonance." },
            { name: "Venus", radius: 1.1, dist: 18, speed: 0.028, color: 0xe8c37d, lore: "Dense carbon dioxide atmosphere with runaway greenhouse heat." },
            { name: "Earth", radius: 1.25, dist: 26, speed: 0.022, color: 0x2878d6, has_moon: true, lore: "The living sapphire jewel: liquid oceans, nitrogen atmosphere, and consciousness." },
            { name: "Mars", radius: 0.75, dist: 34, speed: 0.018, color: 0xd64527, lore: "Rust-red dunes and Olympus Mons: the ancient frontier of water." },
            { name: "Jupiter", radius: 3.4, dist: 52, speed: 0.010, color: 0xc98f4b, has_bands: true, lore: "The gas giant behemoth whose gravity guards the inner terrestrial cradle." },
            { name: "Saturn", radius: 2.8, dist: 74, speed: 0.007, color: 0xe8cb8d, has_rings: true, lore: "Crowned by majestic rings of crystalline water ice and silicates." },
            { name: "Uranus", radius: 1.9, dist: 96, speed: 0.005, color: 0x5297d4, lore: "Ice giant tilted 98 degrees, bathed in methane turquoise." },
            { name: "Neptune", radius: 1.85, dist: 118, speed: 0.004, color: 0x284db0, lore: "Deep azure ice giant swept by 2,000 km/h supersonic winds." }
        ];

        planetaryBodies = [];

        planetConfigs.forEach((p, idx) => {
            const planetPivot = new THREE.Group();

            // Orbital Path Guide Line
            const orbitCurve = new THREE.EllipseCurve(0, 0, p.dist, p.dist, 0, 2 * Math.PI, false, 0);
            const points = orbitCurve.getPoints(64);
            const orbitGeo = new THREE.BufferGeometry().setFromPoints(points);
            const orbitMat = new THREE.LineBasicMaterial({ color: 0x00f3ff, transparent: true, opacity: 0.15 });
            const orbitLine = new THREE.LineLoop(orbitGeo, orbitMat);
            orbitLine.rotation.x = Math.PI / 2;
            solarSystemGroup.add(orbitLine);

            // Planet Mesh
            const pGeo = new THREE.IcosahedronGeometry(p.radius, 2);
            const pMat = new THREE.MeshBasicMaterial({ color: p.color, wireframe: true, transparent: true, opacity: 0.9 });
            const pMesh = new THREE.Mesh(pGeo, pMat);

            // Initial position on orbit
            const initialAngle = (idx * (Math.PI / 4)) + Math.random();
            pMesh.position.set(Math.cos(initialAngle) * p.dist, 0, Math.sin(initialAngle) * p.dist);

            // Saturn Rings
            if (p.has_rings) {
                const ringGeo = new THREE.RingGeometry(p.radius * 1.4, p.radius * 2.5, 32);
                const ringMat = new THREE.MeshBasicMaterial({ color: 0xe8cb8d, side: THREE.DoubleSide, transparent: true, opacity: 0.45 });
                const ringMesh = new THREE.Mesh(ringGeo, ringMat);
                ringMesh.rotation.x = Math.PI / 2.3;
                pMesh.add(ringMesh);
            }

            // Earth Moon
            let moonMesh = null;
            if (p.has_moon) {
                const moonGeo = new THREE.IcosahedronGeometry(0.35, 1);
                const moonMat = new THREE.MeshBasicMaterial({ color: 0xcccccc, wireframe: true });
                moonMesh = new THREE.Mesh(moonGeo, moonMat);
                moonMesh.position.set(2.8, 0.4, 0);
                pMesh.add(moonMesh);
            }

            // Glowing Interaction Halo
            const haloGeo = new THREE.SphereGeometry(p.radius * 1.5, 12, 12);
            const haloMat = new THREE.MeshBasicMaterial({ color: p.color, wireframe: true, transparent: true, opacity: 0.2 });
            const haloMesh = new THREE.Mesh(haloGeo, haloMat);
            pMesh.add(haloMesh);

            pMesh.userData = {
                id: p.name.toLowerCase(),
                name: p.name,
                type: "planet",
                dist: p.dist,
                speed: p.speed,
                angle: initialAngle,
                lore: p.lore,
                color: "#" + p.color.toString(16).padStart(6, "0"),
                mesh: pMesh,
                halo: haloMesh,
                moon: moonMesh
            };

            planetPivot.add(pMesh);
            solarSystemGroup.add(planetPivot);
            planetaryBodies.push(pMesh);
        });

        // 3. Asteroid Belt (2,000 Particles between Mars and Jupiter: radii 38 to 46)
        const astCount = 2000;
        const astGeo = new THREE.BufferGeometry();
        const astPos = new Float32Array(astCount * 3);
        const astCol = new Float32Array(astCount * 3);
        for (let i = 0; i < astCount; i++) {
            const r = 38 + Math.random() * 8;
            const theta = Math.random() * Math.PI * 2;
            const y = (Math.random() - 0.5) * 2.5;
            astPos[i * 3] = Math.cos(theta) * r;
            astPos[i * 3 + 1] = y;
            astPos[i * 3 + 2] = Math.sin(theta) * r;
            astCol[i * 3] = 0.6;
            astCol[i * 3 + 1] = 0.6;
            astCol[i * 3 + 2] = 0.65;
        }
        astGeo.setAttribute("position", new THREE.BufferAttribute(astPos, 3));
        astGeo.setAttribute("color", new THREE.BufferAttribute(astCol, 3));
        const astMat = new THREE.PointsMaterial({ size: 0.8, vertexColors: true, transparent: true, opacity: 0.6 });
        const asteroidBelt = new THREE.Points(astGeo, astMat);
        solarSystemGroup.add(asteroidBelt);

        scene.add(solarSystemGroup);
    }

    /**
     * Scale 3: Milky Way Galaxy (35,000+ Logarithmic Spiral Arm Stars & Sagittarius A* Supermassive Black Hole)
     */
    function createMilkyWayGalaxy(count) {
        if (particleSystem) scene.remove(particleSystem);

        particlesCount = count;
        particlePositions = new Float32Array(count * 3);
        particleVelocities = new Float32Array(count * 3);
        particleColors = new Float32Array(count * 3);

        const palette = PALETTES[activeTheme];
        const arms = 4; // 4 Grand Design Spiral Arms

        for (let i = 0; i < count; i++) {
            const armIndex = i % arms;
            const armOffset = (armIndex * ((Math.PI * 2) / arms));
            const r = Math.pow(Math.random(), 0.55) * 550 + 15;
            const spin = r * 0.015; // Logarithmic spiral winding
            const spread = (Math.random() - 0.5) * (r * 0.18);
            const theta = armOffset + spin + (spread / r);
            const y = (Math.random() - 0.5) * (35 * Math.exp(-r / 350));

            const x = Math.cos(theta) * r;
            const z = Math.sin(theta) * r;

            particlePositions[i * 3] = x;
            particlePositions[i * 3 + 1] = y;
            particlePositions[i * 3 + 2] = z;

            const speed = Math.sqrt(350 / r) * 0.08;
            particleVelocities[i * 3] = -Math.sin(theta) * speed;
            particleVelocities[i * 3 + 1] = (Math.random() - 0.5) * 0.01;
            particleVelocities[i * 3 + 2] = Math.cos(theta) * speed;

            const ratio = r / 550;
            const chosen = ratio < 0.25 ? palette.dust1 : (ratio < 0.65 ? palette.dust2 : palette.dust3);
            particleColors[i * 3] = chosen.r;
            particleColors[i * 3 + 1] = chosen.g;
            particleColors[i * 3 + 2] = chosen.b;
        }

        particleGeometry = new THREE.BufferGeometry();
        particleGeometry.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
        particleGeometry.setAttribute("color", new THREE.BufferAttribute(particleColors, 3));

        const canvas = document.createElement("canvas");
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext("2d");
        const grad = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
        grad.addColorStop(0, "rgba(255,255,255,1)");
        grad.addColorStop(0.3, "rgba(255,255,255,0.7)");
        grad.addColorStop(0.8, "rgba(255,255,255,0.15)");
        grad.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 32, 32);
        const texture = new THREE.CanvasTexture(canvas);

        const particleMaterial = new THREE.PointsMaterial({
            size: isMobile ? 1.6 : 1.3,
            vertexColors: true,
            map: texture,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        particleSystem = new THREE.Points(particleGeometry, particleMaterial);
        scene.add(particleSystem);

        if (microParticles) microParticles.innerText = count.toLocaleString() + " Stars";
    }

    /**
     * Scale 4: Laniakea Galactic Supercluster (Multiple Swirling Spiral Galaxies in Cosmic Ocean)
     */
    function createSuperclusterScale() {
        superclusterGroup = new THREE.Group();

        // 14 Satellite Galaxies in Supercluster
        const galaxyCoordinates = [
            { name: "Andromeda (M31)", x: 850, y: 150, z: -600, color: 0x9d4edd, radius: 140 },
            { name: "Triangulum (M33)", x: -750, y: -200, z: 700, color: 0x00f3ff, radius: 90 },
            { name: "Large Magellanic Cloud", x: 420, y: -350, z: 380, color: 0xff007f, radius: 70 },
            { name: "Small Magellanic Cloud", x: 480, y: -390, z: 420, color: 0xffd166, radius: 50 },
            { name: "Centaurus A", x: -1100, y: 300, z: -900, color: 0x38ef7d, radius: 180 },
            { name: "Virgo Cluster Core (M87)", x: 1400, y: 450, z: 1200, color: 0xff8c00, radius: 240 },
            { name: "Fornax Dwarf", x: -900, y: -450, z: -1100, color: 0x2878d6, radius: 60 }
        ];

        galaxyCoordinates.forEach(g => {
            const gGroup = new THREE.Group();
            gGroup.position.set(g.x, g.y, g.z);

            // Central galaxy bulge
            const bulgeGeo = new THREE.IcosahedronGeometry(g.radius * 0.12, 1);
            const bulgeMat = new THREE.MeshBasicMaterial({ color: g.color, wireframe: true, transparent: true, opacity: 0.6 });
            const bulge = new THREE.Mesh(bulgeGeo, bulgeMat);
            gGroup.add(bulge);

            // Spiral particle disc for satellite galaxy
            const starCount = 350;
            const pos = new Float32Array(starCount * 3);
            for (let i = 0; i < starCount; i++) {
                const r = Math.random() * g.radius;
                const theta = Math.random() * Math.PI * 2 + (r * 0.04);
                pos[i * 3] = Math.cos(theta) * r;
                pos[i * 3 + 1] = (Math.random() - 0.5) * (r * 0.15);
                pos[i * 3 + 2] = Math.sin(theta) * r;
            }
            const sGeo = new THREE.BufferGeometry();
            sGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
            const sMat = new THREE.PointsMaterial({ size: 1.2, color: g.color, transparent: true, opacity: 0.65, blending: THREE.AdditiveBlending });
            const stars = new THREE.Points(sGeo, sMat);
            gGroup.add(stars);

            superclusterGroup.add(gGroup);
        });

        scene.add(superclusterGroup);
    }

    /**
     * Scale 5: Observable Cosmic Web (Dark Matter Neural Filaments)
     */
    function createCosmicWebScale() {
        cosmicWebGroup = new THREE.Group();

        // 3D Filament Web Network connecting macro nodes
        const webNodes = [
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(1200, 400, -900),
            new THREE.Vector3(-1400, -500, 1100),
            new THREE.Vector3(800, -1100, 1600),
            new THREE.Vector3(-1800, 900, -1400),
            new THREE.Vector3(2200, -600, -1800),
            new THREE.Vector3(-2400, 1300, 2100)
        ];

        const lineMat = new THREE.LineBasicMaterial({
            color: 0x9d4edd,
            transparent: true,
            opacity: 0.25,
            blending: THREE.AdditiveBlending
        });

        for (let i = 0; i < webNodes.length; i++) {
            for (let j = i + 1; j < webNodes.length; j++) {
                const pts = [webNodes[i], webNodes[j]];
                const lGeo = new THREE.BufferGeometry().setFromPoints(pts);
                const line = new THREE.Line(lGeo, lineMat);
                cosmicWebGroup.add(line);
            }
        }

        scene.add(cosmicWebGroup);
    }

    /**
     * Interactive Clickable Celestial Beacons
     */
    function createCelestialAnomalies() {
        anomalies = [];

        fetch("/api/lore", { headers: { "ngrok-skip-browser-warning": "true" } })
            .then(res => res.json())
            .then(data => {
                if (data.status === "OK") setupAnomalyMeshes(data.anomalies);
            })
            .catch(() => {
                setupAnomalyMeshes({
                    chrono_weave: { title: "The Chronos Weave", coordinates: [28.5, 12.0, -15.4], color: "#9d4edd", frequency: "432 Hz", sector: "Sector 01-A", lore: "Temporal convergence vortex." },
                    lumina_axon: { title: "The Lumina Axon", coordinates: [-25.2, -8.4, 22.1], color: "#00f3ff", frequency: "528 Hz", sector: "Sector 04-E", lore: "Superluminal neural conduit." },
                    void_singularity: { title: "The Void Singularity", coordinates: [0.0, -22.0, -28.0], color: "#ff007f", frequency: "108 Hz", sector: "Sector 09-X", lore: "Zero-point dissolution." }
                });
            });
    }

    function setupAnomalyMeshes(anomalyData) {
        if (anomaliesList) anomaliesList.innerHTML = "";

        // First list the Sun and major planets
        planetaryBodies.forEach(pMesh => {
            const d = pMesh.userData;
            const row = document.createElement("div");
            row.className = "anomaly-row";
            row.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <span class="anomaly-row-dot" style="background: ${d.color}; box-shadow: 0 0 8px ${d.color};"></span>
                    <div>
                        <div class="anomaly-row-title">${d.name} (${d.dist} AU)</div>
                        <div class="anomaly-row-sector">Solar Orbit • ${d.speed.toFixed(3)} rad/s</div>
                    </div>
                </div>
                <span style="color: var(--cyan); font-size: 0.8rem;">✦</span>
            `;
            row.addEventListener("click", () => {
                closeAllModals();
                selectCelestialTarget(pMesh);
            });
            anomaliesList.appendChild(row);
        });

        // Next list celestial beacons
        Object.keys(anomalyData).forEach((key, index) => {
            const info = anomalyData[key];
            const coords = info.coordinates || [0, 0, 0];
            const colorHex = parseInt(info.color.replace("#", "0x"), 16);

            const beaconMeshGroup = new THREE.Group();
            beaconMeshGroup.position.set(coords[0], coords[1], coords[2]);

            const geo = index % 2 === 0 ? new THREE.OctahedronGeometry(2.5, 1) : new THREE.DodecahedronGeometry(2.2, 0);
            const mat = new THREE.MeshBasicMaterial({ color: colorHex, wireframe: true, transparent: true, opacity: 0.95 });
            const mesh = new THREE.Mesh(geo, mat);
            beaconMeshGroup.add(mesh);

            const haloGeo = new THREE.SphereGeometry(isMobile ? 4.5 : 3.6, 16, 16);
            const haloMat = new THREE.MeshBasicMaterial({ color: colorHex, wireframe: true, transparent: true, opacity: 0.25 });
            const halo = new THREE.Mesh(haloGeo, haloMat);
            beaconMeshGroup.add(halo);

            beaconMeshGroup.userData = {
                id: key,
                name: info.title,
                type: "anomaly",
                title: info.title,
                sector: info.sector || "Cosmic Sector",
                frequency: info.frequency || "432 Hz",
                energy_signature: info.energy_signature || "Stable",
                lore: info.lore || "Cosmic anomaly in deep orbit.",
                color: info.color,
                mesh: mesh,
                halo: halo,
                basePos: new THREE.Vector3(coords[0], coords[1], coords[2]),
                orbitSpeed: 0.003 + (index * 0.001)
            };

            scene.add(beaconMeshGroup);
            anomalies.push(beaconMeshGroup);

            const row = document.createElement("div");
            row.className = "anomaly-row";
            row.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <span class="anomaly-row-dot" style="background: ${info.color}; box-shadow: 0 0 8px ${info.color};"></span>
                    <div>
                        <div class="anomaly-row-title">${info.title}</div>
                        <div class="anomaly-row-sector">${info.sector || "Sector"} • ${info.frequency || "432 Hz"}</div>
                    </div>
                </div>
                <span style="color: var(--cyan); font-size: 0.8rem;">✦</span>
            `;
            row.addEventListener("click", () => {
                closeAllModals();
                selectCelestialTarget(beaconMeshGroup);
            });
            anomaliesList.appendChild(row);
        });
    }

    /**
     * Scale Ribbon Controller (Planet -> Solar System -> Milky Way -> Supercluster -> Cosmic Web)
     */
    function setupScaleRibbon() {
        document.querySelectorAll(".scale-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".scale-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                const scaleKey = btn.dataset.scale;
                transitionToScale(scaleKey);
            });
        });

        if (closeChronicleBtn) {
            closeChronicleBtn.addEventListener("click", () => {
                scaleChronicleCard.classList.add("collapsed");
            });
        }
    }

    function transitionToScale(scaleKey) {
        if (!scaleData[scaleKey]) return;
        currentScale = scaleKey;
        const s = scaleData[scaleKey];

        // Trigger hyperspace sound
        if (window.aetheriaAudio) window.aetheriaAudio.playWarpSound();

        // Macro-Zoom Camera Distance
        const dist = s.dist;
        const currentNorm = camera.position.clone().normalize();
        targetCameraPos = currentNorm.multiplyScalar(dist);
        targetCameraPos.y = dist * 0.35;
        targetLookAt = new THREE.Vector3(0, 0, 0);

        camera.fov = s.fov;
        camera.updateProjectionMatrix();

        // Update Micro Telemetry
        if (microScale) microScale.innerText = "Scale: " + s.badge;

        // Display Scale Chronicle Banner
        if (scaleChronicleCard && scaleBadgeText && scaleChronicleText) {
            scaleBadgeText.innerText = s.badge;
            scaleChronicleText.innerText = `"${s.chronicle}"`;
            scaleChronicleCard.classList.remove("collapsed");
        }

        showToast(`Scale Attuned: ${s.badge}`);
    }

    function selectCelestialTarget(target) {
        selectedTarget = target;
        const data = target.userData;

        closeAllModals();

        if (window.aetheriaAudio) {
            const freqNum = parseFloat(data.frequency) || 432;
            window.aetheriaAudio.playChime(null, freqNum);
        }

        inspectorTitle.innerText = data.name || data.title;
        inspectorTitle.style.color = data.color || "#00f3ff";
        inspectorSector.innerText = data.sector || "Solar Sector";
        inspectorFreq.innerText = data.frequency || "Heliospheric Orbit";
        inspectorEnergy.innerText = data.energy_signature || "Stable World";
        inspectorLore.innerText = data.lore;
        inspectorLore.style.borderLeftColor = data.color || "#00f3ff";
        if (oracleOutput) oracleOutput.style.display = "none";
        inspector.classList.remove("collapsed");

        // Camera smoothly glides to orbit planet/anomaly
        const worldPos = new THREE.Vector3();
        target.getWorldPosition(worldPos);

        const offsetDist = target.userData.type === "planet" ? (target.userData.dist < 30 ? 12 : 22) : (isMobile ? 22 : 18);
        targetCameraPos = worldPos.clone().add(new THREE.Vector3(offsetDist, offsetDist * 0.5, offsetDist));
        targetLookAt = worldPos;
    }

    function onCanvasClick(event) {
        if (event.target.closest(".dynamic-capsule") || event.target.closest(".bottom-dock") || event.target.closest(".scale-ribbon") || event.target.closest(".slide-modal") || event.target.closest(".intro-hook-chip") || event.target.closest(".zen-exit-floating-btn")) {
            return;
        }

        // If in Zen mode, clicking empty space restores UI
        if (isZenMode) {
            exitZenMode();
            return;
        }

        closeAllModals();
        raycaster.setFromCamera(mouse, camera);
        checkRaycastHit();
    }

    function setupTouchInteraction() {
        let touchStartX = 0, touchStartY = 0, touchStartTime = 0;

        window.addEventListener("touchstart", (e) => {
            if (e.touches.length === 1) {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                touchStartTime = performance.now();
            }
        }, { passive: true });

        window.addEventListener("touchend", (e) => {
            if (e.target.closest(".dynamic-capsule") || e.target.closest(".bottom-dock") || e.target.closest(".scale-ribbon") || e.target.closest(".slide-modal") || e.target.closest(".intro-hook-chip") || e.target.closest(".zen-exit-floating-btn")) {
                return;
            }

            if (isZenMode) {
                exitZenMode();
                return;
            }

            if (e.changedTouches.length === 1) {
                const touch = e.changedTouches[0];
                const dx = touch.clientX - touchStartX;
                const dy = touch.clientY - touchStartY;
                const duration = performance.now() - touchStartTime;

                if (Math.hypot(dx, dy) < 15 && duration < 350) {
                    closeAllModals();
                    mouse.x = (touch.clientX / window.innerWidth) * 2 - 1;
                    mouse.y = -(touch.clientY / window.innerHeight) * 2 + 1;
                    raycaster.setFromCamera(mouse, camera);
                    checkRaycastHit();
                }
            }
        });
    }

    function checkRaycastHit() {
        const hitTargets = [];
        planetaryBodies.forEach(p => {
            hitTargets.push(p);
            if (p.userData.halo) hitTargets.push(p.userData.halo);
        });
        anomalies.forEach(grp => {
            hitTargets.push(grp.userData.mesh);
            hitTargets.push(grp.userData.halo);
        });

        const intersects = raycaster.intersectObjects(hitTargets, false);
        if (intersects.length > 0) {
            let hit = intersects[0].object;
            if (hit.parent && hit.parent.userData.type === "anomaly") hit = hit.parent;
            selectCelestialTarget(hit);
        }
    }

    function closeAllModals() {
        if (tuningDeck) tuningDeck.classList.add("collapsed");
        if (anomaliesSheet) anomaliesSheet.classList.add("collapsed");
        if (inspector) inspector.classList.add("collapsed");
        if (scaleChronicleCard) scaleChronicleCard.classList.add("collapsed");
    }

    function onUserActive(event) {
        if (event && event.type === "mousemove") {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        }

        if (introHookChip && !introHookChip.classList.contains("dismissed")) {
            introHookChip.classList.add("dismissed");
        }

        if (isZenMode) return;

        document.body.classList.remove("idle-fade");
        clearTimeout(idleTimer);
        idleTimer = setTimeout(() => {
            if (
                (!tuningDeck || tuningDeck.classList.contains("collapsed")) &&
                (!anomaliesSheet || anomaliesSheet.classList.contains("collapsed")) &&
                (!inspector || inspector.classList.contains("collapsed"))
            ) {
                document.body.classList.add("idle-fade");
            }
        }, 4500);
    }

    function exitZenMode() {
        isZenMode = false;
        document.body.classList.remove("zen-mode");
        const capsuleZenBtn = document.getElementById("capsule-zen-btn");
        if (capsuleZenBtn) capsuleZenBtn.classList.remove("active");
        showToast("Interface Restored");
    }

    function setupErgonomicControls() {
        if (dismissHookBtn) {
            dismissHookBtn.addEventListener("click", () => {
                introHookChip.classList.add("dismissed");
                if (window.aetheriaAudio && !window.aetheriaAudio.isPlaying) toggleAudio();
            });
        }

        // Dedicated Floating Zen Mode Exit Button ("Eye button back on screen")
        if (zenExitBtn) {
            zenExitBtn.addEventListener("click", exitZenMode);
        }

        const capsuleAudioBtn = document.getElementById("capsule-audio-btn");
        const dockAudioBtn = document.getElementById("dock-audio-btn");
        const audioIconSpan = document.getElementById("audio-icon-span");
        const dockAudioIcon = document.getElementById("dock-audio-icon");

        function toggleAudio() {
            const active = window.aetheriaAudio.toggle();
            const icon = active ? "🔊" : "🔇";
            if (audioIconSpan) audioIconSpan.innerText = icon;
            if (dockAudioIcon) dockAudioIcon.innerText = icon;
            if (capsuleAudioBtn) capsuleAudioBtn.classList.toggle("active", active);
            if (dockAudioBtn) dockAudioBtn.classList.toggle("active", active);
            showToast(active ? "432 Hz Soundscape Engaged" : "Soundscape Suspended");
        }

        if (capsuleAudioBtn) capsuleAudioBtn.addEventListener("click", toggleAudio);
        if (dockAudioBtn) dockAudioBtn.addEventListener("click", toggleAudio);

        const capsuleWarpBtn = document.getElementById("capsule-warp-btn");
        const dockWarpBtn = document.getElementById("dock-warp-btn");
        if (capsuleWarpBtn) capsuleWarpBtn.addEventListener("click", triggerWarpJump);
        if (dockWarpBtn) dockWarpBtn.addEventListener("click", triggerWarpJump);

        const capsuleZenBtn = document.getElementById("capsule-zen-btn");
        if (capsuleZenBtn) {
            capsuleZenBtn.addEventListener("click", () => {
                isZenMode = !isZenMode;
                document.body.classList.toggle("zen-mode", isZenMode);
                capsuleZenBtn.classList.toggle("active", isZenMode);
                showToast(isZenMode ? "Pure Zen View Engaged • Tap Eye to Restore" : "Interface Restored");
            });
        }

        const dockExploreBtn = document.getElementById("dock-explore-btn");
        if (dockExploreBtn) {
            dockExploreBtn.addEventListener("click", () => {
                closeAllModals();
                transitionToScale("solar_system");
            });
        }

        const dockAnomaliesBtn = document.getElementById("dock-anomalies-btn");
        const closeAnomaliesBtn = document.getElementById("close-anomalies-btn");
        if (dockAnomaliesBtn && anomaliesSheet) {
            dockAnomaliesBtn.addEventListener("click", () => {
                const isClosed = anomaliesSheet.classList.contains("collapsed");
                closeAllModals();
                if (isClosed) anomaliesSheet.classList.remove("collapsed");
            });
        }
        if (closeAnomaliesBtn && anomaliesSheet) closeAnomaliesBtn.addEventListener("click", () => anomaliesSheet.classList.add("collapsed"));

        const dockTuneBtn = document.getElementById("dock-tune-btn");
        const closeTuningBtn = document.getElementById("close-tuning-btn");
        if (dockTuneBtn && tuningDeck) {
            dockTuneBtn.addEventListener("click", () => {
                const isClosed = tuningDeck.classList.contains("collapsed");
                closeAllModals();
                if (isClosed) tuningDeck.classList.remove("collapsed");
            });
        }
        if (closeTuningBtn && tuningDeck) closeTuningBtn.addEventListener("click", () => tuningDeck.classList.add("collapsed"));

        const closeInspectorBtn = document.getElementById("close-inspector-btn");
        if (closeInspectorBtn && inspector) closeInspectorBtn.addEventListener("click", () => inspector.classList.add("collapsed"));

        document.querySelectorAll(".theme-pill").forEach(pill => {
            pill.addEventListener("click", () => {
                document.querySelectorAll(".theme-pill").forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                switchTheme(pill.dataset.theme);
            });
        });

        const speedSlider = document.getElementById("speed-slider");
        const speedVal = document.getElementById("speed-val");
        if (speedSlider) {
            speedSlider.addEventListener("input", (e) => {
                speedMult = parseFloat(e.target.value);
                speedVal.innerText = speedMult.toFixed(1) + "x";
            });
        }

        const gravitySlider = document.getElementById("gravity-slider");
        const gravityVal = document.getElementById("gravity-val");
        if (gravitySlider) {
            gravitySlider.addEventListener("input", (e) => {
                gravityMult = parseFloat(e.target.value);
                gravityVal.innerText = gravityMult.toFixed(1) + "x";
            });
        }

        const resetCamBtn = document.getElementById("reset-cam-btn");
        if (resetCamBtn) {
            resetCamBtn.addEventListener("click", () => {
                transitionToScale(currentScale);
                closeAllModals();
            });
        }

        const snapshotBtn = document.getElementById("snapshot-btn");
        if (snapshotBtn) snapshotBtn.addEventListener("click", captureScreenshot);

        const oracleForm = document.getElementById("oracle-form");
        const oracleInput = document.getElementById("oracle-input");
        if (oracleForm && oracleInput) {
            oracleForm.addEventListener("submit", (e) => {
                e.preventDefault();
                const text = oracleInput.value.trim();
                if (!text) return;

                const name = selectedTarget ? (selectedTarget.userData.name || selectedTarget.userData.title) : "Cosmic Core";
                oracleOutput.style.display = "block";
                oracleOutput.innerText = "Transmitting to NVIDIA Nemotron Oracle across the quantum void...";

                if (window.aetheriaAudio) window.aetheriaAudio.playChime(3);
                oracleInput.blur();

                fetch("/api/transmit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "ngrok-skip-browser-warning": "true" },
                    body: jsonString({ prompt: text, anomaly: name })
                })
                .then(res => res.json())
                .then(data => {
                    oracleOutput.innerText = `"${data.response}"`;
                    if (window.aetheriaAudio) window.aetheriaAudio.playChime(6);
                })
                .catch(err => {
                    oracleOutput.innerText = "Cosmic flux disrupted: " + err.message;
                });
            });
        }
    }

    function switchTheme(theme) {
        if (!PALETTES[theme]) return;
        activeTheme = theme;
        const pal = PALETTES[theme];

        scene.fog.color.setHex(pal.fog);
        renderer.setClearColor(pal.fog, 1);

        if (window.aetheriaAudio) window.aetheriaAudio.setMode(theme);
        createMilkyWayGalaxy(particlesCount);
        showToast(`Theme Attuned: ${theme.toUpperCase()}`);
    }

    function triggerWarpJump() {
        if (isWarping) return;
        isWarping = true;
        closeAllModals();
        showToast("WARP JUMP INITIATED");

        if (window.aetheriaAudio) window.aetheriaAudio.playWarpSound();

        let start = performance.now();
        let duration = 2200;

        function warpStep(now) {
            let elapsed = now - start;
            let progress = elapsed / duration;

            if (progress < 0.5) {
                warpFactor = 1.0 + (progress * 2) * 12.0;
            } else if (progress < 1.0) {
                warpFactor = 13.0 - ((progress - 0.5) * 2) * 12.0;
            } else {
                warpFactor = 1.0;
                isWarping = false;
                const angle = Math.random() * Math.PI * 2;
                targetCameraPos = new THREE.Vector3(Math.cos(angle) * 120, 35 + Math.random() * 20, Math.sin(angle) * 120);
                targetLookAt = new THREE.Vector3(0, 0, 0);
                showToast("DROPPED OUT OF WARP IN NEW SECTOR");
                return;
            }

            requestAnimationFrame(warpStep);
        }

        requestAnimationFrame(warpStep);
    }

    function captureScreenshot() {
        renderer.render(scene, camera);
        const dataURL = renderer.domElement.toDataURL("image/png");
        const link = document.createElement("a");
        link.download = `Aetheria_Cosmos_${Date.now()}.png`;
        link.href = dataURL;
        link.click();
        showToast("Cosmic Snapshot Saved to Downloads");
    }

    function showToast(msg) {
        const toast = document.getElementById("toast-notice");
        if (!toast) return;
        toast.innerText = msg;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 2800);
    }

    function jsonString(obj) {
        return JSON.stringify(obj);
    }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    /**
     * Ultra-Smooth 240 FPS Main Animation Loop (Delta-Time Normalized Physics)
     */
    function animate(time) {
        requestAnimationFrame(animate);

        // Delta-Time calculation for variable refresh rates (60Hz to 240Hz+)
        const delta = Math.min(clock.getDelta(), 0.05); // cap at 20fps minimum to avoid tunnel penetration
        const timeScale = delta * 60.0; // 1.0 at 60fps, 0.25 at 240fps

        // High-Refresh FPS Telemetry
        frameCount++;
        if (time - lastFpsTime >= 1000) {
            currentFps = Math.round((frameCount * 1000) / (time - lastFpsTime));
            if (capsuleFps) capsuleFps.innerText = currentFps + " FPS";
            if (microFps) microFps.innerText = currentFps + " FPS Ultra-Smooth";
            frameCount = 0;
            lastFpsTime = time;
        }

        const effSpeed = speedMult * warpFactor * timeScale;
        const audioEnergy = window.aetheriaAudio ? window.aetheriaAudio.getEnergy() : 0;

        // 1. Cinematic Ingress on startup
        if (isIngress) {
            const elapsed = time - ingressStart;
            const progress = Math.min(1.0, elapsed / ingressDuration);
            const ease = 1 - Math.pow(1 - progress, 3);
            camera.position.lerpVectors(startPos, targetOrbitPos, ease);
            controls.target.set(0, 0, 0);
            if (progress >= 1.0) isIngress = false;
        }

        // 2. Animate Solar System Planets in Keplerian Orbits
        planetaryBodies.forEach((pMesh) => {
            const d = pMesh.userData;
            d.angle += d.speed * 0.5 * effSpeed;
            pMesh.position.x = Math.cos(d.angle) * d.dist;
            pMesh.position.z = Math.sin(d.angle) * d.dist;
            pMesh.rotation.y += 0.02 * effSpeed;

            // Animate Moon around Earth
            if (d.moon) {
                const moonAngle = time * 0.003 * effSpeed;
                d.moon.position.x = Math.cos(moonAngle) * 2.8;
                d.moon.position.z = Math.sin(moonAngle) * 2.8;
            }
        });

        // 3. Animate Celestial Beacons
        anomalies.forEach((grp) => {
            const d = grp.userData;
            const angle = time * d.orbitSpeed * 0.001 * effSpeed;
            grp.position.x = Math.cos(angle) * d.basePos.x - Math.sin(angle) * d.basePos.z;
            grp.position.z = Math.sin(angle) * d.basePos.x + Math.cos(angle) * d.basePos.z;
            grp.position.y = d.basePos.y + Math.sin(time * 0.002) * 1.5;

            d.mesh.rotation.y += 0.02 * effSpeed;
            d.mesh.rotation.x += 0.015 * effSpeed;
            d.halo.rotation.z -= 0.01 * effSpeed;
        });

        // 4. Animate Milky Way Galactic Spiral
        if (particleGeometry && particlePositions) {
            const pos = particlePositions;
            const vel = particleVelocities;
            const count = particlesCount;

            for (let i = 0; i < count; i++) {
                const i3 = i * 3;
                let px = pos[i3];
                let py = pos[i3 + 1];
                let pz = pos[i3 + 2];

                px += vel[i3] * effSpeed;
                py += vel[i3 + 1] * effSpeed;
                pz += vel[i3 + 2] * effSpeed;

                const distSq = px * px + py * py + pz * pz;
                if (distSq > 150) {
                    const pull = (0.04 * gravityMult) / Math.sqrt(distSq);
                    vel[i3] -= (px / Math.sqrt(distSq)) * pull;
                    vel[i3 + 2] -= (pz / Math.sqrt(distSq)) * pull;
                }

                if (isWarping) pz += vel[i3 + 2] * (warpFactor * 2.5);

                if (distSq > 450000) {
                    px *= 0.25;
                    pz *= 0.25;
                }

                pos[i3] = px;
                pos[i3 + 1] = py;
                pos[i3 + 2] = pz;
            }
            particleGeometry.attributes.position.needsUpdate = true;
        }

        // 5. Rotate Superclusters and Cosmic Web slowly
        if (superclusterGroup) superclusterGroup.rotation.y += 0.0003 * effSpeed;
        if (cosmicWebGroup) cosmicWebGroup.rotation.y += 0.0001 * effSpeed;

        // 6. Frame-Independent Exponential Camera Smoothing (Silky 240 FPS Lerp)
        if (targetCameraPos && !isIngress) {
            const lerpFactor = 1.0 - Math.exp(-6.0 * delta);
            camera.position.lerp(targetCameraPos, lerpFactor);
            currentLookAt.lerp(targetLookAt, lerpFactor);
            controls.target.copy(currentLookAt);
            if (camera.position.distanceTo(targetCameraPos) < 0.2) {
                targetCameraPos = null;
            }
        }

        controls.update();
        renderer.render(scene, camera);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

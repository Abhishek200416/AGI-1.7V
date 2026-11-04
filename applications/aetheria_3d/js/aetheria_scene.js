/**
 * AETHERIA 3D • Universal Scale Journey (240 FPS Ultra-Smooth Engine)
 * =============================================================================
 * Real Astrophysical Universe & Organic Bubble Multiverse:
 *
 * 1. ZERO BOXES: The Multiverse is rendered as real hyperspherical Bubble Universes
 *    and cosmic void spaces connected by quantum gravitational filaments.
 * 2. Real Rotation & Revolution:
 *    - True Keplerian OVAL (elliptical) orbits with eccentricity, perihelion acceleration,
 *      and aphelion deceleration.
 *    - Real planetary axial tilts (obliquity): Earth (23.4°), Mars (25.2°), Saturn (26.7°),
 *      Uranus (97.8°), with continuous axial rotation while revolving!
 * 3. The Colossal Blue Hypergiant (Cygnus Leviathan):
 *    - 10 times larger than our Solar System (Radius 65 units), blazing with incandescent
 *      cyan-blue thermonuclear plasma and dynamic firing coronal flares!
 *    - Carries our Sun (Helios Prime) and multiple sister solar systems revolving around
 *      it in massive oval orbits!
 * 4. Living Fire & Relativistic Plasma (NO DEAD BLACK):
 *    - Sagittarius A* surrounded by molten fiery red-orange relativistic accretion plasma
 *      with Doppler beaming and polar plasma jets.
 *    - Dynamic pulsating solar prominences and convective stellar atmospheres.
 * 5. 65,000+ Stars with Pure Analytical Rotation:
 *    - Zero shaking, zero vibration, zero square pixels (Gaussian soft radial sprites).
 * =============================================================================
 */

(function () {
    let scene, camera, renderer, controls, clock;
    let universeRoot;
    let blueHypergiant, blueHypergiantGroup;
    let hgGalacticRadius = Math.sqrt(2800 * 2800 + 1900 * 1900); // ~3383.78 units from Sgr A*
    let hgGalacticAngle = Math.atan2(1900, 2800); // ~0.5964 radians
    let solOrbitPivot, solSystemGroup, earthMesh, earthClouds, moonMesh;
    let sisterSystemsGroup = [];
    let milkyWayGroup, sgrAccretionDisk, sgrJetNorth, sgrJetSouth;
    let superclusterGroup, cosmicWebGroup, bubbleMultiverseGroup;

    // Collections of interactive celestial objects
    let planetaryBodies = [];
    let stellarObjects = [];
    let bubbleUniverses = [];
    let selectedTarget = null;

    // Particle simulation
    let particlesCount = 125000;
    let particlePositions, particlePhases, particleRadii, particleSpeeds, particleGeometry, particleSystem;
    let starSize = 1.6;
    let galaxySpeedMult = 1.0;

    // Raycasting & Interaction
    let raycaster, mouse;
    let activeTheme = "violet";
    let speedMult = 1.0;
    let isWarping = false;
    let warpFactor = 1.0;
    let soundEnabled = true;

    // Device detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;

    // Camera target for smooth lerp
    let targetCameraPos = null;
    let targetLookAt = new THREE.Vector3(0, 0, 0);
    let currentLookAt = new THREE.Vector3(0, 0, 0);
    let prevSunPos = new THREE.Vector3();
    let focusedObject = null;
    let prevFocusPos = new THREE.Vector3();
    const activeKeys = {};
    let hoverReticle = null;

    // Dynamic Scale Thresholds (Camera Distance -> Cosmological Tier)
    const SCALE_TIERS = [
        { maxDist: 38, key: "planetary", badge: "🌍 Terrestrial Close-Up (10^7 m)", chronicle: "A living sapphire jewel: liquid oceans, continents, and delicate atmospheres cradling life." },
        { maxDist: 260, key: "solar_system", badge: "☀️ Heliosphere Solar System (10^13 m)", chronicle: "A radiant stellar furnace carrying eight worlds and rocky belts in harmonious Keplerian flight." },
        { maxDist: 2400, key: "stellar_neighborhood", badge: "💎 Cygnus Blue Hypergiant (10^17 m)", chronicle: "A colossal blue hypergiant 10x larger than our solar system, carrying stellar families in majestic oval orbits." },
        { maxDist: 18000, key: "milky_way", badge: "🌌 Milky Way Spiral & Sgr A* (10^21 m)", chronicle: "A grand design spiral arm of starlight swirling around Sagittarius A*, burning with relativistic plasma." },
        { maxDist: 85000, key: "supercluster", badge: "🌀 Laniakea Mega-Cluster & 16 Galaxy Clusters (10^24 m)", chronicle: "Thousands of galaxies across 16 major clusters flowing along gravitational rivers toward the Great Attractor." },
        { maxDist: 600000, key: "cosmic_web", badge: "🕸️ Observable Cosmic Web & Boötes Voids (10^26 m)", chronicle: "A cosmic sponge of dark matter filaments weaving around vast silent abyssal supervoids." },
        { maxDist: Infinity, key: "multiverse_matrix", badge: "🫧 Infinite Bubble Multiverse & Omniverse (10^29 m)", chronicle: "Infinite hyperspherical bubble universes nucleating within the quantum inflaton ocean across millions of light-years." }
    ];
    let detectedScaleKey = "solar_system";

    // Ingress Animation (Centered on Helios Prime & Our 8 Planets)
    let isIngress = true;
    let ingressStart = performance.now();
    let ingressDuration = 2200;
    const sunInitWorldX = 2800 + 412.8;
    const sunInitWorldY = 40;
    const sunInitWorldZ = 1900;
    const startPos = new THREE.Vector3(sunInitWorldX, sunInitWorldY + 38, sunInitWorldZ + 98);
    const targetOrbitPos = new THREE.Vector3(sunInitWorldX, sunInitWorldY + 30, sunInitWorldZ + 86);

    // Zen Mode
    let idleTimer = null;
    let isZenMode = false;

    // High-Refresh 240 FPS Telemetry & Sub-Stepping Physics
    let lastFpsTime = performance.now();
    let frameCount = 0;
    let currentFps = 60;
    let targetFpsSetting = 240;
    let fixedPhysicsDt = 1.0 / 240.0;
    let physicsAccumulator = 0;

    // DOM Elements
    const container = document.getElementById("canvas-container");
    const capsuleFps = document.getElementById("capsule-fps");
    const microParticles = document.getElementById("micro-particles");
    const microScale = document.getElementById("micro-scale");
    const microFps = document.getElementById("micro-fps");
    const introHookChip = document.getElementById("intro-hook-chip");
    const dismissHookBtn = document.getElementById("dismiss-hook-btn");
    const zenExitBtn = document.getElementById("zen-exit-floating-btn");

    const scaleChronicleCard = document.getElementById("scale-chronicle-card");
    const scaleBadgeText = document.getElementById("scale-badge-text");
    const scaleChronicleText = document.getElementById("scale-chronicle-text");
    const closeChronicleBtn = document.getElementById("close-chronicle-btn");

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
            fog: 0x03040a
        },
        aurora: {
            core: 0x38ef7d,
            ring: 0x11998e,
            dust1: new THREE.Color(0x11998e),
            dust2: new THREE.Color(0x38ef7d),
            dust3: new THREE.Color(0x00f3ff),
            fog: 0x010c0e
        },
        solar: {
            core: 0xff4500,
            ring: 0xffd166,
            dust1: new THREE.Color(0xff4500),
            dust2: new THREE.Color(0xffa200),
            dust3: new THREE.Color(0xffd166),
            fog: 0x0e0602
        },
        void: {
            core: 0x718096,
            ring: 0x4a5568,
            dust1: new THREE.Color(0xa0aec0),
            dust2: new THREE.Color(0x4a5568),
            dust3: new THREE.Color(0x2d3748),
            fog: 0x010204
        }
    };

    /* =========================================================================
       PROCEDURAL CANVAS TEXTURE GENERATORS (100% Solid & Fiery • Zero Wireframes)
       ========================================================================= */

    function createGaussianStarTexture() {
        const c = document.createElement("canvas");
        c.width = 64; c.height = 64;
        const ctx = c.getContext("2d");
        const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
        grad.addColorStop(0.0, "rgba(255, 255, 255, 1.0)");
        grad.addColorStop(0.25, "rgba(255, 250, 235, 0.92)");
        grad.addColorStop(0.55, "rgba(160, 215, 255, 0.35)");
        grad.addColorStop(0.85, "rgba(80, 140, 255, 0.08)");
        grad.addColorStop(1.0, "rgba(0, 0, 0, 0.0)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 64, 64);
        return new THREE.CanvasTexture(c);
    }

    function createBlueHypergiantTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");

        // Incandescent electric cyan-blue convective thermonuclear surface (40,000 K)
        const grad = ctx.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0, "#0077b6");
        grad.addColorStop(0.3, "#00b4d8");
        grad.addColorStop(0.5, "#90e0ef");
        grad.addColorStop(0.7, "#00b4d8");
        grad.addColorStop(1, "#0077b6");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1024, 512);

        // Supersonic turbulent plasma granules
        for (let i = 0; i < 450; i++) {
            const x = Math.random() * 1024;
            const y = Math.random() * 512;
            const r = 12 + Math.random() * 45;
            ctx.fillStyle = Math.random() > 0.4 ? "rgba(255, 255, 255, 0.55)" : "rgba(0, 243, 255, 0.4)";
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fill();
        }

        return new THREE.CanvasTexture(c);
    }

    function createSunTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");

        // Fiery golden-orange convective photosphere
        const grad = ctx.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0, "#d9480f");
        grad.addColorStop(0.35, "#f59f00");
        grad.addColorStop(0.5, "#ffd43b");
        grad.addColorStop(0.65, "#f59f00");
        grad.addColorStop(1, "#d9480f");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1024, 512);

        for (let i = 0; i < 400; i++) {
            const x = Math.random() * 1024;
            const y = Math.random() * 512;
            const r = 10 + Math.random() * 35;
            ctx.fillStyle = Math.random() > 0.5 ? "rgba(255, 243, 191, 0.45)" : "rgba(232, 89, 12, 0.45)";
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fill();
        }

        return new THREE.CanvasTexture(c);
    }

    function createRedSupergiantTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");

        // Boiling ruby-red and crimson convective granulation
        const grad = ctx.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0, "#7f1d1d");
        grad.addColorStop(0.4, "#dc2626");
        grad.addColorStop(0.5, "#f87171");
        grad.addColorStop(0.6, "#dc2626");
        grad.addColorStop(1, "#7f1d1d");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1024, 512);

        for (let i = 0; i < 350; i++) {
            const x = Math.random() * 1024;
            const y = Math.random() * 512;
            const r = 18 + Math.random() * 55;
            ctx.fillStyle = Math.random() > 0.5 ? "rgba(254, 202, 202, 0.4)" : "rgba(153, 27, 27, 0.5)";
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fill();
        }

        return new THREE.CanvasTexture(c);
    }

    function createEarthTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");

        const oceanGrad = ctx.createLinearGradient(0, 0, 0, 512);
        oceanGrad.addColorStop(0, "#08214d");
        oceanGrad.addColorStop(0.5, "#0e3b7e");
        oceanGrad.addColorStop(1, "#08214d");
        ctx.fillStyle = oceanGrad;
        ctx.fillRect(0, 0, 1024, 512);

        function drawContinent(points, color, strokeColor) {
            ctx.fillStyle = color;
            ctx.strokeStyle = strokeColor || color;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(points[0][0], points[0][1]);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i][0], points[i][1]);
            }
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        }

        drawContinent([[120, 90], [240, 70], [310, 120], [280, 200], [210, 220], [180, 260], [140, 210], [90, 140]], "#2d6a4f");
        drawContinent([[240, 240], [330, 280], [320, 390], [270, 460], [230, 360], [210, 270]], "#1e4620");
        drawContinent([[460, 80], [680, 60], [860, 100], [830, 220], [720, 260], [620, 220], [520, 240], [450, 150]], "#344e41");
        drawContinent([[460, 220], [580, 220], [610, 310], [560, 420], [490, 420], [440, 290]], "#b08968");
        drawContinent([[470, 230], [570, 230], [560, 280], [460, 270]], "#ddb892"); // Sahara
        drawContinent([[780, 340], [870, 340], [880, 420], [810, 440], [770, 380]], "#b05d3b"); // Australia

        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, 1024, 38);
        ctx.fillRect(0, 474, 1024, 38);

        return new THREE.CanvasTexture(c);
    }

    function createEarthCloudTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");
        ctx.clearRect(0, 0, 1024, 512);

        ctx.fillStyle = "rgba(255, 255, 255, 0.75)";
        for (let i = 0; i < 75; i++) {
            const x = Math.random() * 1024;
            const y = 80 + Math.random() * 350;
            const rw = 60 + Math.random() * 140;
            const rh = 12 + Math.random() * 32;
            ctx.beginPath();
            ctx.ellipse(x, y, rw, rh, Math.random() * 0.4 - 0.2, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.strokeStyle = "rgba(255, 255, 255, 0.88)";
        ctx.lineWidth = 14;
        ctx.beginPath();
        ctx.arc(280, 180, 35, 0, Math.PI * 1.6);
        ctx.stroke();

        return new THREE.CanvasTexture(c);
    }

    function createMarsTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");

        const grad = ctx.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0, "#8a280b");
        grad.addColorStop(0.5, "#bd3a13");
        grad.addColorStop(1, "#8a280b");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1024, 512);

        ctx.fillStyle = "#4a190b";
        ctx.beginPath();
        ctx.ellipse(512, 260, 160, 75, 0.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(320, 290, 120, 45, -0.15, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.ellipse(512, 18, 110, 18, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(512, 494, 90, 18, 0, 0, Math.PI * 2);
        ctx.fill();

        return new THREE.CanvasTexture(c);
    }

    function createJupiterTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");

        const colors = ["#d4a373", "#e9ecef", "#b08968", "#6f4e37", "#ddb892", "#7f4f24", "#ede0d4", "#c68b59"];
        const bandH = 512 / colors.length;
        colors.forEach((col, idx) => {
            ctx.fillStyle = col;
            ctx.fillRect(0, idx * bandH, 1024, bandH);
        });

        ctx.fillStyle = "#a61e1e";
        ctx.beginPath();
        ctx.ellipse(620, 340, 65, 38, -0.08, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "rgba(255, 255, 255, 0.35)";
        ctx.beginPath();
        ctx.arc(620, 340, 22, 0, Math.PI * 2);
        ctx.fill();

        return new THREE.CanvasTexture(c);
    }

    function createSaturnTexture() {
        const c = document.createElement("canvas");
        c.width = 1024; c.height = 512;
        const ctx = c.getContext("2d");

        const grad = ctx.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0, "#e8d5b5");
        grad.addColorStop(0.3, "#d9c39e");
        grad.addColorStop(0.5, "#eed9b7");
        grad.addColorStop(0.7, "#d4be98");
        grad.addColorStop(1, "#e8d5b5");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1024, 512);

        return new THREE.CanvasTexture(c);
    }

    function createSaturnRingsTexture() {
        const c = document.createElement("canvas");
        c.width = 512; c.height = 64;
        const ctx = c.getContext("2d");

        const grad = ctx.createLinearGradient(0, 0, 512, 0);
        grad.addColorStop(0.00, "rgba(180, 160, 130, 0.15)");
        grad.addColorStop(0.18, "rgba(220, 200, 160, 0.40)");
        grad.addColorStop(0.32, "rgba(240, 220, 180, 0.95)");
        grad.addColorStop(0.60, "rgba(245, 225, 185, 0.90)");
        grad.addColorStop(0.62, "rgba(0, 0, 0, 0.0)");        // Sharp Cassini Division!
        grad.addColorStop(0.67, "rgba(0, 0, 0, 0.0)");
        grad.addColorStop(0.69, "rgba(215, 195, 160, 0.85)");
        grad.addColorStop(0.88, "rgba(190, 170, 140, 0.70)");
        grad.addColorStop(0.90, "rgba(0, 0, 0, 0.0)");        // Encke Gap
        grad.addColorStop(0.93, "rgba(175, 155, 125, 0.45)");
        grad.addColorStop(1.00, "rgba(0, 0, 0, 0.0)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 512, 64);

        return new THREE.CanvasTexture(c);
    }

    function createMoonTexture() {
        const c = document.createElement("canvas");
        c.width = 512; c.height = 256;
        const ctx = c.getContext("2d");
        ctx.fillStyle = "#8d99ae";
        ctx.fillRect(0, 0, 512, 256);

        ctx.fillStyle = "#495057";
        ctx.beginPath();
        ctx.ellipse(180, 110, 65, 45, 0.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(320, 140, 80, 55, -0.1, 0, Math.PI * 2);
        ctx.fill();

        for (let i = 0; i < 40; i++) {
            ctx.fillStyle = "#ced4da";
            ctx.beginPath();
            ctx.arc(Math.random() * 512, Math.random() * 256, 3 + Math.random() * 8, 0, Math.PI * 2);
            ctx.fill();
        }
        return new THREE.CanvasTexture(c);
    }

    /* =========================================================================
       INITIALIZATION & SCENE SETUP
       ========================================================================= */

    function init() {
        clock = new THREE.Clock();

        if (isMobile) {
            particlesCount = 42000;
        }

        // 1. Scene & Deep Void Fog
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(PALETTES.violet.fog, 0.000004);

        // 2. Camera: Extreme Infinite Dynamic Range (0.1 to 10,000,000 units)
        camera = new THREE.PerspectiveCamera(58, window.innerWidth / window.innerHeight, 0.1, 10000000);
        camera.position.copy(startPos);

        // 3. WebGL Renderer with Logarithmic Depth Buffer
        renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: "high-performance",
            precision: "highp",
            logarithmicDepthBuffer: true,
            preserveDrawingBuffer: true
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.35;
        container.appendChild(renderer.domElement);

        // 4. Orbit Controls (Unrestricted Infinite Macro-Zoom)
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 1.0;
        controls.maxDistance = 5000000;
        controls.target.set(sunInitWorldX, sunInitWorldY, sunInitWorldZ);
        currentLookAt.set(sunInitWorldX, sunInitWorldY, sunInitWorldZ);
        targetLookAt.set(sunInitWorldX, sunInitWorldY, sunInitWorldZ);
        controls.touches = {
            ONE: THREE.TOUCH.ROTATE,
            TWO: THREE.TOUCH.DOLLY_PAN
        };

        // 5. Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
        scene.add(ambientLight);

        // 6. Master Universe Hierarchy Root
        universeRoot = new THREE.Group();
        scene.add(universeRoot);

        // Raycasting
        raycaster = new THREE.Raycaster();
        raycaster.params.Points.threshold = 2.0;
        mouse = new THREE.Vector2(-999, -999);

        // 7. BUILD UNIFIED COSMIC ARCHITECTURE
        createBlueHypergiantAndSystems();
        createMilkyWayGalaxy(particlesCount);
        createSuperclusterScale();
        createCosmicWebScale();
        createBubbleMultiverseScale();
        loadSystemCatalog();

        // 8. Event Listeners
        window.addEventListener("resize", onWindowResize);
        window.addEventListener("mousemove", onUserActive);
        window.addEventListener("touchstart", onUserActive, { passive: true });
        window.addEventListener("click", onCanvasClick);

        setupTouchInteraction();
        setupScaleRibbon();
        setupErgonomicControls();
        setupKeyboardFlightControls();
        setupHoverReticle();

        window._aetheria = { scene, camera, controls, solSystemGroup, blueHypergiant };

        scene.updateMatrixWorld(true);
        ingressStart = performance.now();
        animate(performance.now());
    }

    /* =========================================================================
       CYGNUS LEVIATHAN (BLUE HYPERGIANT 10X BIGGER) & NESTED SOLAR SYSTEMS
       ========================================================================= */

    function createBlueHypergiantAndSystems() {
        blueHypergiantGroup = new THREE.Group();
        // Positioned in the Orion-Cygnus Arm of the Milky Way Galaxy
        blueHypergiantGroup.position.set(2800, 40, 1900);
        universeRoot.add(blueHypergiantGroup);

        // 1. The Colossal Blue Hypergiant Star: Cygnus Leviathan
        // Radius: 65 units (10x larger than our Sun!)
        const hgGeo = new THREE.SphereGeometry(65, 64, 64);
        const hgMat = new THREE.MeshBasicMaterial({ map: createBlueHypergiantTexture(), color: 0x90e0ef });
        blueHypergiant = new THREE.Mesh(hgGeo, hgMat);
        blueHypergiant.position.set(0, 0, 0);
        blueHypergiant.rotation.z = THREE.MathUtils.degToRad(14.0); // Axial tilt

        // Blazing Electric Cyan Coronal Flare Envelope
        const hgHaloGeo = new THREE.SphereGeometry(95, 32, 32);
        const hgHaloMat = new THREE.MeshBasicMaterial({
            color: 0x00f3ff,
            transparent: true,
            opacity: 0.38,
            blending: THREE.AdditiveBlending,
            side: THREE.BackSide
        });
        blueHypergiant.add(new THREE.Mesh(hgHaloGeo, hgHaloMat));

        // Pulsating Volumetric Solar Prominences Ring
        const flareRingGeo = new THREE.RingGeometry(68, 110, 64);
        const flareRingMat = new THREE.MeshBasicMaterial({
            color: 0x00d4ff,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.45,
            blending: THREE.AdditiveBlending
        });
        const flareRing = new THREE.Mesh(flareRingGeo, flareRingMat);
        flareRing.rotation.x = Math.PI / 2.3;
        blueHypergiant.add(flareRing);

        const hgLight = new THREE.PointLight(0x00e5ff, 7.5, 4500);
        blueHypergiant.add(hgLight);

        blueHypergiant.userData = {
            id: "cygnus_blue_hypergiant",
            name: "Cygnus Leviathan (Blue Hypergiant)",
            type: "blue_hypergiant",
            sector: "Orion-Cygnus Arm • 3,500 LY",
            frequency: "741.00 Hz",
            energy_signature: "40,000 K O-Type Stellar Behemoth",
            lore: "A colossal blue hypergiant ten times larger than our solar system, blazing with incandescent cyan thermonuclear fire and carrying multiple complete solar systems in its gravitational embrace.",
            color: "#00f3ff",
            mesh: blueHypergiant
        };
        blueHypergiantGroup.add(blueHypergiant);
        stellarObjects.push(blueHypergiant);

        // 2. HELIOS PRIME (OUR SOLAR SYSTEM): Revolves in an OVAL (Elliptical) Orbit around Blue Hypergiant!
        solOrbitPivot = new THREE.Group();
        blueHypergiantGroup.add(solOrbitPivot);

        solSystemGroup = new THREE.Group();
        solOrbitPivot.add(solSystemGroup);

        // Real Oval (Elliptical) Orbit Parameters for Our Sun: a = 480, e = 0.14
        const solSemiA = 480;
        const solEcc = 0.14;
        buildOvalOrbitLine(blueHypergiantGroup, solSemiA, solEcc, 0xffa200);

        const solInitR = (solSemiA * (1 - solEcc * solEcc)) / (1 + solEcc);
        solSystemGroup.position.set(solInitR, 0, 0);

        // Our Sun: Blazing Golden Photosphere + Prominences
        const sunGeo = new THREE.SphereGeometry(6.5, 48, 48);
        const sunMat = new THREE.MeshBasicMaterial({ map: createSunTexture(), color: 0xfff0c2 });
        const sunMesh = new THREE.Mesh(sunGeo, sunMat);
        sunMesh.rotation.z = THREE.MathUtils.degToRad(7.25); // Solar axial tilt
        solSystemGroup.add(sunMesh);

        // Fiery Golden Solar Flare Corona
        const sunCoronaGeo = new THREE.SphereGeometry(9.2, 32, 32);
        const sunCoronaMat = new THREE.MeshBasicMaterial({
            color: 0xffaa22,
            transparent: true,
            opacity: 0.35,
            blending: THREE.AdditiveBlending,
            side: THREE.BackSide
        });
        sunMesh.add(new THREE.Mesh(sunCoronaGeo, sunCoronaMat));

        const solLight = new THREE.PointLight(0xfffaed, 4.5, 550);
        sunMesh.add(solLight);

        sunMesh.userData = {
            id: "sol",
            name: "Helios Prime (Our Sun)",
            type: "star_system",
            sector: "Orion Spur • Heliosphere",
            frequency: "528.00 Hz",
            energy_signature: "G2V Main Sequence Fusion Engine",
            lore: "Our parent yellow dwarf star, carrying Earth and seven sibling worlds in orbital flight around the Cygnus Leviathan.",
            color: "#ffa200",
            mesh: sunMesh,
            semiA: solSemiA,
            ecc: solEcc,
            angle: 0.0,
            baseSpeed: 0.0032
        };
        stellarObjects.push(sunMesh);

        // Build 8 Real Planets with Authentic Axial Tilts & Oval Keplerian Orbits
        buildOurOvalPlanets(solSystemGroup);

        // 3. SISTER SOLAR SYSTEMS CARRIED BY THE BLUE HYPERGIANT
        buildSisterSystemsAroundHypergiant(blueHypergiantGroup);
    }

    function buildOvalOrbitLine(parentGroup, a, e, colorHex) {
        const points = [];
        const segments = 128;
        for (let i = 0; i <= segments; i++) {
            const theta = (i / segments) * Math.PI * 2;
            const r = (a * (1 - e * e)) / (1 + e * Math.cos(theta));
            points.push(new THREE.Vector3(Math.cos(theta) * r, 0, Math.sin(theta) * r));
        }
        const geo = new THREE.BufferGeometry().setFromPoints(points);
        const mat = new THREE.LineBasicMaterial({ color: colorHex, transparent: true, opacity: 0.22 });
        parentGroup.add(new THREE.LineLoop(geo, mat));
    }

    function buildOurOvalPlanets(parentGroup) {
        const planetConfigs = [
            { name: "Mercury", radius: 0.55, a: 15, ecc: 0.205, speed: 0.038, tilt: 0.03, color: "#9e9e9e", lore: "Sun-scorched iron world with extreme perihelion temperature swings." },
            { name: "Venus", radius: 1.15, a: 22, ecc: 0.007, speed: 0.028, tilt: 177.3, color: "#e8c37d", lore: "Shrouded in dense carbon dioxide with runaway greenhouse heat and retrograde rotation." },
            { name: "Earth", radius: 1.35, a: 32, ecc: 0.017, speed: 0.022, tilt: 23.44, color: "#2878d6", is_earth: true, has_moon: true, lore: "The living sapphire jewel: liquid oceans, continents, independent swirling clouds, and life." },
            { name: "Mars", radius: 0.78, a: 44, ecc: 0.093, speed: 0.018, tilt: 25.19, color: "#bd3a13", is_mars: true, lore: "Rust-red iron oxide dunes, Olympus Mons, Valles Marineris, and frozen white polar ice caps." },
            { name: "Jupiter", radius: 3.6, a: 76, ecc: 0.048, speed: 0.010, tilt: 3.13, color: "#c98f4b", is_jupiter: true, lore: "The grand gas giant whose caramel storm belts and Great Red Spot shield the inner planets." },
            { name: "Saturn", radius: 3.0, a: 104, ecc: 0.054, speed: 0.007, tilt: 26.73, color: "#e8cb8d", is_saturn: true, lore: "Crowned by photorealistic concentric rings of crystalline water ice with the dark Cassini Division." },
            { name: "Uranus", radius: 1.9, a: 132, ecc: 0.047, speed: 0.005, tilt: 97.77, color: "#5297d4", is_uranus: true, lore: "Pale turquoise ice giant tilted 98 degrees, revolving on its side with vertical faint rings." },
            { name: "Neptune", radius: 1.85, a: 160, ecc: 0.009, speed: 0.004, tilt: 28.32, color: "#284db0", lore: "Deep azure ice giant swept by supersonic storm winds and high-altitude cirrus streaks." }
        ];

        planetConfigs.forEach((p, idx) => {
            // Draw real oval Keplerian orbit guide line
            buildOvalOrbitLine(parentGroup, p.a, p.ecc, 0x00f3ff);

            // Planet Axial Tilt Group
            const tiltGroup = new THREE.Group();
            tiltGroup.rotation.z = THREE.MathUtils.degToRad(p.tilt);

            // Planet Mesh Geometry
            const pGeo = new THREE.SphereGeometry(p.radius, 48, 48);
            let pMat;

            if (p.is_earth) {
                pMat = new THREE.MeshStandardMaterial({ map: createEarthTexture(), roughness: 0.7 });
            } else if (p.is_mars) {
                pMat = new THREE.MeshStandardMaterial({ map: createMarsTexture(), roughness: 0.85 });
            } else if (p.is_jupiter) {
                pMat = new THREE.MeshStandardMaterial({ map: createJupiterTexture(), roughness: 0.9 });
            } else if (p.is_saturn) {
                pMat = new THREE.MeshStandardMaterial({ map: createSaturnTexture(), roughness: 0.9 });
            } else {
                pMat = new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.8 });
            }

            const pMesh = new THREE.Mesh(pGeo, pMat);
            tiltGroup.add(pMesh);

            // Earth Independent Rotating Cloud Layer & Moon
            if (p.is_earth) {
                earthMesh = pMesh;
                const cloudGeo = new THREE.SphereGeometry(p.radius * 1.025, 48, 48);
                const cloudMat = new THREE.MeshStandardMaterial({ map: createEarthCloudTexture(), transparent: true, opacity: 0.85, depthWrite: false });
                earthClouds = new THREE.Mesh(cloudGeo, cloudMat);
                pMesh.add(earthClouds);

                const atmoGeo = new THREE.SphereGeometry(p.radius * 1.08, 32, 32);
                const atmoMat = new THREE.MeshBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, side: THREE.BackSide });
                pMesh.add(new THREE.Mesh(atmoGeo, atmoMat));
            }

            // Saturn Rings (Tilted with Saturn's 26.7° obliquity)
            if (p.is_saturn) {
                const ringGeo = new THREE.RingGeometry(p.radius * 1.45, p.radius * 2.8, 64);
                const ringMat = new THREE.MeshBasicMaterial({ map: createSaturnRingsTexture(), side: THREE.DoubleSide, transparent: true, opacity: 0.92 });
                const ringMesh = new THREE.Mesh(ringGeo, ringMat);
                ringMesh.rotation.x = Math.PI / 2.35;
                pMesh.add(ringMesh);
            }

            // Uranus Rings (Vertical tilt)
            if (p.is_uranus) {
                const uRingGeo = new THREE.RingGeometry(p.radius * 1.3, p.radius * 1.8, 48);
                const uRingMat = new THREE.MeshBasicMaterial({ color: 0xa0e7e5, side: THREE.DoubleSide, transparent: true, opacity: 0.45 });
                const uRingMesh = new THREE.Mesh(uRingGeo, uRingMat);
                uRingMesh.rotation.y = Math.PI / 2.1;
                pMesh.add(uRingMesh);
            }

            // Moon Orbiting Earth
            if (p.has_moon) {
                const moonGeo = new THREE.SphereGeometry(0.38, 24, 24);
                const moonMat = new THREE.MeshStandardMaterial({ map: createMoonTexture(), roughness: 0.9 });
                moonMesh = new THREE.Mesh(moonGeo, moonMat);
                moonMesh.position.set(3.4, 0.4, 0);
                tiltGroup.add(moonMesh);
            }

            const initialAngle = (idx * (Math.PI / 4)) + Math.random();
            const initR = (p.a * (1 - p.ecc * p.ecc)) / (1 + p.ecc * Math.cos(initialAngle));
            tiltGroup.position.set(Math.cos(initialAngle) * initR, 0, Math.sin(initialAngle) * initR);

            tiltGroup.userData = {
                id: p.name.toLowerCase(),
                name: p.name,
                type: "planet",
                a: p.a,
                ecc: p.ecc,
                speed: p.speed,
                angle: initialAngle,
                lore: p.lore,
                color: p.color,
                mesh: pMesh,
                tiltGroup: tiltGroup,
                moon: moonMesh
            };

            parentGroup.add(tiltGroup);
            planetaryBodies.push(tiltGroup);
        });

        // Asteroid Belt (3,000 Rocky Particles)
        const astCount = 3000;
        const astGeo = new THREE.BufferGeometry();
        const astPos = new Float32Array(astCount * 3);
        const astCol = new Float32Array(astCount * 3);
        for (let i = 0; i < astCount; i++) {
            const a = 54 + Math.random() * 14;
            const theta = Math.random() * Math.PI * 2;
            const r = a * (1 - 0.08 * Math.cos(theta));
            astPos[i * 3] = Math.cos(theta) * r;
            astPos[i * 3 + 1] = (Math.random() - 0.5) * 3.5;
            astPos[i * 3 + 2] = Math.sin(theta) * r;
            const shade = 0.5 + Math.random() * 0.3;
            astCol[i * 3] = shade; astCol[i * 3 + 1] = shade * 0.92; astCol[i * 3 + 2] = shade * 0.85;
        }
        astGeo.setAttribute("position", new THREE.BufferAttribute(astPos, 3));
        astGeo.setAttribute("color", new THREE.BufferAttribute(astCol, 3));
        const astMat = new THREE.PointsMaterial({
            size: 0.85,
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            map: createGaussianStarTexture(),
            depthWrite: false
        });
        parentGroup.add(new THREE.Points(astGeo, astMat));
    }

    function buildSisterSystemsAroundHypergiant(parentGroup) {
        // Complete 31 Sister Solar Systems Revolving in Oval Orbits around Cygnus Leviathan (32 total systems with Helios Prime)
        const systems = [
            {
                id: "rigel_system",
                name: "Rigel Major (Luminous Blue-White Supergiant)",
                a: 540, ecc: 0.12, angle: 0.45, baseSpeed: 0.0024, starColor: "#bae6fd", starRadius: 12.0,
                planets: [
                    { name: "Rigel b (Ocean Prime)", a: 28, ecc: 0.05, radius: 1.4, color: "#38ef7d", lore: "An azure ocean world with atmospheric water vapor." },
                    { name: "Rigel c (Chrono-Desert)", a: 45, ecc: 0.12, radius: 1.1, color: "#ffd166", lore: "A golden desert exoplanet rich in heavy silicates." },
                    { name: "Rigel d (Ice Sovereign)", a: 68, ecc: 0.08, radius: 2.2, color: "#a0e7e5", lore: "A majestic frozen gas dwarf shrouded in methane cirrus clouds." }
                ],
                lore: "A brilliant B8 supergiant blazing with 120,000 times solar luminosity, carrying its planetary family in a broad elliptical orbit."
            },
            {
                id: "betelgeuse_system",
                name: "Betelgeuse Crimson (Boiling Red Supergiant)",
                a: 620, ecc: 0.15, angle: 1.25, baseSpeed: 0.0020, starColor: "#ef4444", starRadius: 20.0, is_red_supergiant: true,
                planets: [
                    { name: "Betelgeuse Prime (Lava World)", a: 38, ecc: 0.08, radius: 1.6, color: "#f97316", lore: "A molten magma planet bathed in the boiling convective flares of Betelgeuse." },
                    { name: "Betelgeuse b (Obsidian Core)", a: 65, ecc: 0.14, radius: 1.4, color: "#78350f", lore: "A high-density scorched planet with liquid basalt rivers." }
                ],
                lore: "A colossal pulsating red supergiant undergoing massive mass-loss episodes, illuminating its outer planets with crimson light."
            },
            {
                id: "trappist_system",
                name: "TRAPPIST-1 Resonant Cradle",
                a: 710, ecc: 0.18, angle: 2.05, baseSpeed: 0.0018, starColor: "#ff007f", starRadius: 4.5,
                planets: [
                    { name: "TRAPPIST-1b (Vapour World)", a: 11, ecc: 0.03, radius: 0.75, color: "#fb7185", lore: "A dense steam world with a perpetual superheated atmosphere." },
                    { name: "TRAPPIST-1c (Rocky Basalt)", a: 15, ecc: 0.02, radius: 0.85, color: "#fdba74", lore: "A tidally locked rocky world with deep iron canyons." },
                    { name: "TRAPPIST-1e (Habitable Earth Twin)", a: 21, ecc: 0.02, radius: 1.25, color: "#00f3ff", lore: "An Earth-sized world in the habitable zone harboring liquid water." },
                    { name: "TRAPPIST-1f (Global Ice World)", a: 32, ecc: 0.06, radius: 1.1, color: "#bae6fd", lore: "A frozen cryo-biosphere shrouded in high-albedo ice sheets." }
                ],
                lore: "An ultra-cool red dwarf system carrying tightly packed resonant terrestrial exoplanets."
            },
            {
                id: "kepler452_system",
                name: "Kepler-452 (Golden Sun Twin)",
                a: 790, ecc: 0.08, angle: 2.85, baseSpeed: 0.0016, starColor: "#facc15", starRadius: 7.2,
                planets: [
                    { name: "Kepler-452b (Earth's Elder Cousin)", a: 34, ecc: 0.04, radius: 1.55, color: "#22c55e", lore: "A super-Earth orbiting within the habitable zone of its G2V parent star." },
                    { name: "Kepler-452c (Azure Gas Dwarf)", a: 58, ecc: 0.09, radius: 2.3, color: "#06b6d4", lore: "A mini-Neptune rich in hydrogen, helium, and atmospheric water droplets." }
                ],
                lore: "A mature solar twin star system six billion years old, sheltering life-bearing orbital architectures."
            },
            {
                id: "gliese667_system",
                name: "Gliese 667C (Triple Star Red Dwarf)",
                a: 870, ecc: 0.14, angle: 3.65, baseSpeed: 0.0015, starColor: "#f87171", starRadius: 4.8,
                planets: [
                    { name: "Gliese 667Cc (Super-Earth Eden)", a: 16, ecc: 0.03, radius: 1.35, color: "#10b981", lore: "A world receiving warm red sunlight, crowned with vibrant chlorophyll oceans." },
                    { name: "Gliese 667Ce (Tidally Locked Desert)", a: 26, ecc: 0.08, radius: 1.1, color: "#f59e0b", lore: "A crimson-illuminated desert planet with everlasting dawn and twilight bands." },
                    { name: "Gliese 667Cf (Glacial Oasis)", a: 38, ecc: 0.11, radius: 1.2, color: "#93c5fd", lore: "An icy outer refuge with geothermal hydrothermal vents under surface ice." }
                ],
                lore: "A member of a triple-star system holding multiple super-Earth candidates in resonance."
            },
            {
                id: "vega_system",
                name: "Vega Lyrae (Blazing Blue-White Star)",
                a: 950, ecc: 0.07, angle: 4.35, baseSpeed: 0.0014, starColor: "#e0f2fe", starRadius: 9.8,
                planets: [
                    { name: "Vega b (Jovian Giant)", a: 36, ecc: 0.05, radius: 2.9, color: "#38bdf8", lore: "A colossal gas giant that carves the inner edge of Vega's famous circumstellar debris disk." },
                    { name: "Vega c (Cometary Swarm World)", a: 64, ecc: 0.14, radius: 1.3, color: "#c084fc", lore: "A silicated world pelted continuously by cometary bombardment in the outer halo." }
                ],
                lore: "The fifth brightest star in Earth's sky, spinning so fast it is oblate and surrounded by dust rings."
            },
            {
                id: "sirius_system",
                name: "Sirius A & B (The Rainbow Star System)",
                a: 1030, ecc: 0.19, angle: 5.15, baseSpeed: 0.0013, starColor: "#ffffff", starRadius: 8.9,
                planets: [
                    { name: "Sirius B (White Dwarf Companion)", a: 22, ecc: 0.25, radius: 1.2, color: "#e2e8f0", lore: "The dense degenerate Earth-sized core of a collapsed former giant star." },
                    { name: "Sirius c (Heliosphere Outpost)", a: 52, ecc: 0.08, radius: 1.6, color: "#67e8f9", lore: "A crystalline ice-shrouded world reflecting blinding white light." }
                ],
                lore: "The brightest star in the night sky, accompanied by the famous white dwarf Pup."
            },
            {
                id: "polaris_system",
                name: "Polaris North (Yellow Supergiant)",
                a: 1110, ecc: 0.06, angle: 0.85, baseSpeed: 0.0012, starColor: "#fef08a", starRadius: 13.5,
                planets: [
                    { name: "Polaris Ab (Companion Dwarf)", a: 24, ecc: 0.06, radius: 1.9, color: "#fde047", lore: "A close stellar companion bathed in the pulsating envelope of the Cepheid variable." },
                    { name: "Polaris b (Permafrost Giant)", a: 56, ecc: 0.10, radius: 2.7, color: "#6ee7b7", lore: "A massive gas giant whose moons experience periodic variations in stellar brightness." }
                ],
                lore: "The classical North Star, a pulsating classical Cepheid supergiant navigating our northern skies."
            },
            {
                id: "aldebaran_system",
                name: "Aldebaran Taurus (Fiery Orange Giant)",
                a: 1190, ecc: 0.11, angle: 1.65, baseSpeed: 0.0011, starColor: "#fb923c", starRadius: 15.5,
                planets: [
                    { name: "Aldebaran b (Thermal Jovian)", a: 42, ecc: 0.09, radius: 3.3, color: "#ea580c", lore: "A gas giant six times more massive than Jupiter, radiating deep orange heat." },
                    { name: "Aldebaran c (Molten Titanium World)", a: 22, ecc: 0.15, radius: 1.25, color: "#dc2626", lore: "A close-in terrestrial planet with atmospheric clouds of vaporized silicates and metals." }
                ],
                lore: "The fiery Eye of Taurus, an evolved red giant forty-four times the solar diameter."
            },
            {
                id: "antares_system",
                name: "Antares Heart (The Scorpion Supergiant)",
                a: 1270, ecc: 0.16, angle: 2.45, baseSpeed: 0.0010, starColor: "#dc2626", starRadius: 23.0, is_red_supergiant: true,
                planets: [
                    { name: "Antares Companion B (Emerald Star)", a: 30, ecc: 0.12, radius: 3.6, color: "#10b981", lore: "A blazing blue-green B2.5 dwarf companion embedded within Antares' stellar envelope." },
                    { name: "Antares c (Wind-Scoured World)", a: 62, ecc: 0.18, radius: 1.8, color: "#f43f5e", lore: "A barren rocky planet shaped by the torrential mass-loss winds of the dying supergiant." }
                ],
                lore: "Rival of Mars, a gigantic M-supergiant so vast it would swallow the orbit of Mars if placed in our solar system."
            },
            {
                id: "proxima_system",
                name: "Proxima Centauri (Our Nearest Neighbor)",
                a: 1350, ecc: 0.21, angle: 3.25, baseSpeed: 0.0010, starColor: "#ef4444", starRadius: 3.9,
                planets: [
                    { name: "Proxima b (Habitable Haven)", a: 12, ecc: 0.04, radius: 1.08, color: "#34d399", lore: "A rocky terrestrial exoplanet orbiting within the star's habitable equilibrium zone." },
                    { name: "Proxima c (Sub-Neptune Ringed)", a: 32, ecc: 0.12, radius: 1.85, color: "#818cf8", lore: "A cold gas mini-giant crowned by expansive dusty rings." }
                ],
                lore: "The closest star to our Solar System at 4.24 light-years, harboring terrestrial habitable candidates."
            },
            {
                id: "tauceti_system",
                name: "Tau Ceti (Pristine Solar Analogue)",
                a: 1420, ecc: 0.08, angle: 4.05, baseSpeed: 0.00095, starColor: "#fde047", starRadius: 5.9,
                planets: [
                    { name: "Tau Ceti e (Super-Earth Biosphere)", a: 24, ecc: 0.05, radius: 1.38, color: "#059669", lore: "A serene planet with lush liquid oceans and dense, breathable atmosphere." },
                    { name: "Tau Ceti f (Outermost Tundra)", a: 46, ecc: 0.09, radius: 1.42, color: "#60a5fa", lore: "A glaciated world at the outer edge of the system's habitable perimeter." }
                ],
                lore: "A quiet, stable yellow dwarf star known for its exceptionally calm stellar magnetic activity."
            },
            {
                id: "epsilon_system",
                name: "Epsilon Eridani (Young Dusty System)",
                a: 1490, ecc: 0.11, angle: 4.85, baseSpeed: 0.00090, starColor: "#f59e0b", starRadius: 6.1,
                planets: [
                    { name: "AEgir (Jovian Ringed Giant)", a: 35, ecc: 0.07, radius: 2.6, color: "#d97706", lore: "A mighty gas giant shepherding the vast internal asteroid and dust belts." },
                    { name: "Epsilon Dust World", a: 19, ecc: 0.16, radius: 1.05, color: "#a8a29e", lore: "A cratered silicate planet navigating between active planetesimal rings." }
                ],
                lore: "A young planetary system resembling our own Solar System during its early Late Heavy Bombardment epoch."
            },
            {
                id: "hd209458_system",
                name: "HD 209458 (Osiris Hot Jupiter)",
                a: 1560, ecc: 0.09, angle: 5.65, baseSpeed: 0.00085, starColor: "#fef08a", starRadius: 6.7,
                planets: [
                    { name: "Osiris b (Evaporating Jovian)", a: 15, ecc: 0.02, radius: 2.3, color: "#38bdf8", lore: "A gas giant boiling under intense stellar radiation, trailing a majestic cometary tail." },
                    { name: "Osiris c (Silicate Core)", a: 34, ecc: 0.08, radius: 1.25, color: "#fbbf24", lore: "A warm terrestrial planet enriched in carbon and silicate minerals." }
                ],
                lore: "The first transiting exoplanet ever discovered, where atmospheric water and carbon were first detected."
            },
            {
                id: "cancri55_system",
                name: "55 Cancri (Diamond Carbon Star)",
                a: 1630, ecc: 0.13, angle: 0.35, baseSpeed: 0.00082, starColor: "#fef9c3", starRadius: 6.3,
                planets: [
                    { name: "Janssen (Super-Earth Diamond)", a: 12, ecc: 0.05, radius: 1.15, color: "#e0e7ff", lore: "A scorching super-Earth composed primarily of carbon in the form of diamond and graphite." },
                    { name: "Galileo (Ocean Jovian)", a: 30, ecc: 0.08, radius: 2.8, color: "#0284c7", lore: "A gas giant covered in deep liquid water layers beneath a hydrogen canopy." }
                ],
                lore: "A five-planet system showcasing unprecedented chemical diversity and carbon-rich exoplanets."
            },
            {
                id: "wolf1061_system",
                name: "Wolf 1061 (Red Dwarf Sentinel)",
                a: 1700, ecc: 0.16, angle: 1.15, baseSpeed: 0.00078, starColor: "#ef4444", starRadius: 4.1,
                planets: [
                    { name: "Wolf 1061c (Super-Earth Haven)", a: 17, ecc: 0.04, radius: 1.28, color: "#4ade80", lore: "A rocky world within the goldilocks zone with mild temperatures and liquid water." },
                    { name: "Wolf 1061d (Dense Ice Giant)", a: 38, ecc: 0.12, radius: 1.95, color: "#93c5fd", lore: "A deep blue cryogenic gas planet swept by perpetual blizzards." }
                ],
                lore: "A tranquil red dwarf located only 14 light-years away from Earth."
            },
            {
                id: "ross128_system",
                name: "Ross 128 (Peaceful Habitable Haven)",
                a: 1770, ecc: 0.07, angle: 1.95, baseSpeed: 0.00075, starColor: "#f87171", starRadius: 4.3,
                planets: [
                    { name: "Ross 128b (Temperate Paradise)", a: 16, ecc: 0.03, radius: 1.14, color: "#2dd4bf", lore: "A benign world with surface temperatures comparable to Earth and no lethal stellar flares." }
                ],
                lore: "An exceptionally quiet red dwarf star lacking superflares, making its planet a prime candidate for life."
            },
            {
                id: "trappist9_system",
                name: "TRAPPIST-9 (Alien Resonance Realm)",
                a: 1840, ecc: 0.14, angle: 2.75, baseSpeed: 0.00072, starColor: "#d946ef", starRadius: 4.6,
                planets: [
                    { name: "Chrono-1 (Quantum Crystal World)", a: 14, ecc: 0.05, radius: 1.05, color: "#c084fc", lore: "A world composed of crystalline silicate lattices resonating with magnetic harmonics." },
                    { name: "Chrono-2 (Supersymmetric Habitable)", a: 27, ecc: 0.08, radius: 1.22, color: "#a855f7", lore: "A living biome nurtured by exotic low-energy magnetic flux fields." }
                ],
                lore: "An enigmatic alien star system whose orbital periods follow Fibonacci harmonic resonances."
            },
            {
                id: "cygnus_x_system",
                name: "Cygnus X-Prime (High-Energy Blue Star)",
                a: 1910, ecc: 0.19, angle: 3.55, baseSpeed: 0.00070, starColor: "#00f3ff", starRadius: 16.5,
                planets: [
                    { name: "Cygnus X-1b (Iron Shell Planet)", a: 36, ecc: 0.12, radius: 1.85, color: "#67e8f9", lore: "A metal-rich dense world stripped of its lighter volatile mantle." },
                    { name: "Cygnus X-1c (Plasma Torus Jovian)", a: 62, ecc: 0.15, radius: 3.1, color: "#06b6d4", lore: "A massive gas giant generating an ionized plasma ring around the hypergiant." }
                ],
                lore: "A massive, energetic O-type star blazing with blinding blue-violet thermonuclear brilliance."
            },
            {
                id: "kepler22_system",
                name: "Kepler-22 (The Waterworld Sovereign)",
                a: 1980, ecc: 0.06, angle: 4.35, baseSpeed: 0.00067, starColor: "#bef264", starRadius: 6.5,
                planets: [
                    { name: "Kepler-22b (The Global Ocean World)", a: 29, ecc: 0.02, radius: 1.95, color: "#0ea5e9", lore: "A boundless global ocean planet devoid of dry land, with deep-sea thermal biodiversity." },
                    { name: "Kepler-22c (Deep Storm Giant)", a: 54, ecc: 0.09, radius: 2.5, color: "#2563eb", lore: "An azure ice giant roaring with planet-wide equatorial hurricane bands." }
                ],
                lore: "Host of the historic first confirmed habitable zone exoplanet discovered by NASA's Kepler Mission."
            },
            {
                id: "wolf359_system",
                name: "Wolf 359 (The Flare Dwarf)",
                a: 2050, ecc: 0.22, angle: 5.15, baseSpeed: 0.00065, starColor: "#b91c1c", starRadius: 3.6,
                planets: [
                    { name: "Wolf 359b (Radioactive Basalt)", a: 11, ecc: 0.18, radius: 0.95, color: "#991b1b", lore: "A scorched obsidian world scarred by violent thermonuclear magnetic eruptions." },
                    { name: "Wolf 359c (Frozen Ammonia World)", a: 28, ecc: 0.14, radius: 1.35, color: "#c4b5fd", lore: "A glaciated planet coated in frozen methane and ammonia snowdrifts." }
                ],
                lore: "One of the faintest and lowest-mass stars known, famous for its energetic flare outbursts."
            },
            {
                id: "fomalhaut_system",
                name: "Fomalhaut (Eye of Sauron Star)",
                a: 2120, ecc: 0.12, angle: 0.65, baseSpeed: 0.00062, starColor: "#bae6fd", starRadius: 10.5,
                planets: [
                    { name: "Dagon (Circumstellar Jovian)", a: 40, ecc: 0.09, radius: 2.95, color: "#0284c7", lore: "A colossal planet swimming inside the luminous glowing dust ring of Fomalhaut." },
                    { name: "Fomalhaut Dust Shepherd", a: 68, ecc: 0.14, radius: 1.45, color: "#94a3b8", lore: "A terrestrial world maintaining the razor-sharp outer boundary of the dust ring." }
                ],
                lore: "The Eye of Sauron, encircled by a dramatic glowing ring of cometary debris 140 AU wide."
            },
            {
                id: "spica_system",
                name: "Spica Virginis (Spectroscopic Blue Binary)",
                a: 2190, ecc: 0.15, angle: 1.45, baseSpeed: 0.00060, starColor: "#38bdf8", starRadius: 12.5,
                planets: [
                    { name: "Spica Companion Star", a: 19, ecc: 0.10, radius: 3.1, color: "#0284c7", lore: "A rapid orbital companion engaged in a four-day tidal gravitational waltz." },
                    { name: "Spica c (Irradiated Jovian)", a: 48, ecc: 0.15, radius: 2.7, color: "#818cf8", lore: "A massive gas giant whose nightside glows with fluorescent auroral currents." }
                ],
                lore: "A pulsating beta Cepheid variable star shining with 20,000 times the visual luminosity of our Sun."
            },
            {
                id: "deneb_system",
                name: "Deneb Cygnus (Alpha Cygni White Supergiant)",
                a: 2260, ecc: 0.07, angle: 2.25, baseSpeed: 0.00058, starColor: "#f8fafc", starRadius: 18.5,
                planets: [
                    { name: "Deneb b (Luminous Gas Crown)", a: 50, ecc: 0.06, radius: 3.5, color: "#f1f5f9", lore: "A gigantic white-hued Jovian basking in the unyielding radiance of Deneb." },
                    { name: "Deneb c (Frozen Nitrogen World)", a: 78, ecc: 0.11, radius: 1.85, color: "#cbd5e1", lore: "A terrestrial world covered in solid nitrogen sheets and frozen lakes." }
                ],
                lore: "One of the most distant naked-eye stars, a powerhouse supergiant 200 times the Sun's diameter."
            },
            {
                id: "canopus_system",
                name: "Canopus Carina (The Great White Giant)",
                a: 2330, ecc: 0.09, angle: 3.05, baseSpeed: 0.00055, starColor: "#fef08a", starRadius: 15.5,
                planets: [
                    { name: "Canopus b (Gold Sand World)", a: 38, ecc: 0.08, radius: 1.75, color: "#fde047", lore: "A world of endless golden quartz dunes and sparkling silicate dust storms." },
                    { name: "Canopus c (Aurora Ice Giant)", a: 66, ecc: 0.12, radius: 2.85, color: "#5eead4", lore: "A turquoise Jovian displaying brilliant coronal auroral halos across both poles." }
                ],
                lore: "The second-brightest star in Earth's night sky, a vital navigational beacon for interplanetary spacecraft."
            },
            {
                id: "arcturus_system",
                name: "Arcturus Bootis (Ancient Orange Giant)",
                a: 2400, ecc: 0.14, angle: 3.85, baseSpeed: 0.00053, starColor: "#ea580c", starRadius: 16.5,
                planets: [
                    { name: "Arcturus b (Hot Metal Core)", a: 32, ecc: 0.10, radius: 1.95, color: "#f97316", lore: "A rocky planet stripped to its molten core by the intense stellar luminosity." },
                    { name: "Arcturus c (Sovereign Jovian)", a: 60, ecc: 0.15, radius: 3.2, color: "#c2410c", lore: "A Jovian gas world holding a family of 48 icy captured moons." }
                ],
                lore: "An ancient giant star from the galactic halo passing through our local spiral arm at 122 km/s."
            },
            {
                id: "pollux_system",
                name: "Pollux Gemini (The Twin Giant)",
                a: 2470, ecc: 0.08, angle: 4.65, baseSpeed: 0.00051, starColor: "#f59e0b", starRadius: 11.5,
                planets: [
                    { name: "Thestias (Massive Super-Jupiter)", a: 36, ecc: 0.06, radius: 3.4, color: "#d97706", lore: "A confirmed exoplanet 2.3 times the mass of Jupiter in a circular 590-day orbit." }
                ],
                lore: "The closest giant star to the Sun, holding the proud distinction of harboring the confirmed planet Thestias."
            },
            {
                id: "castor_system",
                name: "Castor Gemini (The Sextuple Star Cradle)",
                a: 2540, ecc: 0.18, angle: 5.45, baseSpeed: 0.00049, starColor: "#a5f3fc", starRadius: 8.8,
                planets: [
                    { name: "Castor Ba (Orbital Binary)", a: 24, ecc: 0.12, radius: 2.8, color: "#38bdf8", lore: "A companion A-type star sharing a complex gravitational choreography." },
                    { name: "Castor c (Hex-Resonant World)", a: 54, ecc: 0.16, radius: 1.55, color: "#a78bfa", lore: "A terrestrial world whose sky contains six distinct suns at dawn and dusk." }
                ],
                lore: "A remarkable sextuple star system consisting of three pairs of binary stars orbiting one another."
            },
            {
                id: "achernar_system",
                name: "Achernar Eridani (The Oblate High-Speed Spinner)",
                a: 2610, ecc: 0.11, angle: 0.95, baseSpeed: 0.00047, starColor: "#06b6d4", starRadius: 13.5,
                planets: [
                    { name: "Achernar b (Equatorial Gas Torus)", a: 34, ecc: 0.08, radius: 2.6, color: "#0891b2", lore: "A gaseous mini-planet embedded within the star's hot equatorial ejection disk." },
                    { name: "Achernar c (Polar Frozen Biosphere)", a: 60, ecc: 0.14, radius: 1.45, color: "#22d3ee", lore: "A terrestrial world facing the cooler polar regions of the oblate star." }
                ],
                lore: "The least spherical star known: rotating at 250 km/s, its equatorial diameter is 56% greater than its poles."
            },
            {
                id: "alcyone_system",
                name: "Alcyone Pleiades (The Seven Sisters Jewel)",
                a: 2680, ecc: 0.13, angle: 1.75, baseSpeed: 0.00045, starColor: "#3b82f6", starRadius: 10.8,
                planets: [
                    { name: "Maia Prime (Nebular Mirror)", a: 35, ecc: 0.09, radius: 1.85, color: "#60a5fa", lore: "A serene planet reflecting the sapphire-blue reflection nebula of the Pleiades." },
                    { name: "Electra Oasis (Crystalline Biosphere)", a: 58, ecc: 0.13, radius: 1.55, color: "#2563eb", lore: "A world of quartz mountains and fluorescent bioluminescent oceans." }
                ],
                lore: "The luminous anchor of the Pleiades open cluster, enveloped in glowing reflection nebulae."
            },
            {
                id: "chronos_minor_system",
                name: "Chronos Leviathan Minor (Sub-Hypergiant)",
                a: 2750, ecc: 0.16, angle: 2.55, baseSpeed: 0.00043, starColor: "#c084fc", starRadius: 14.5,
                planets: [
                    { name: "Chronos-Alpha (Gravity-Bent Jovian)", a: 40, ecc: 0.11, radius: 2.8, color: "#a855f7", lore: "A massive gas giant whose rings refract light into relativistic rainbows." },
                    { name: "Chronos-Beta (Habitable Super-Earth)", a: 65, ecc: 0.15, radius: 1.65, color: "#38ef7d", lore: "A lush super-Earth warmed by both Cygnus Leviathan and its host star." }
                ],
                lore: "The outermost sister star system revolving at the extreme gravitational boundary of the Cygnus Leviathan."
            }
        ];

        systems.forEach(sys => {
            // Draw oval orbit line around Cygnus Leviathan
            buildOvalOrbitLine(parentGroup, sys.a, sys.ecc, sys.starColor);

            const sysPivot = new THREE.Group();
            parentGroup.add(sysPivot);

            const sysGroup = new THREE.Group();
            sysPivot.add(sysGroup);

            // Primary Star of Sister System
            const sGeo = new THREE.SphereGeometry(sys.starRadius, 32, 32);
            const sTexture = sys.is_red_supergiant ? createRedSupergiantTexture() : createSunTexture();
            const sMat = new THREE.MeshBasicMaterial({ map: sTexture, color: sys.starColor });
            const starMesh = new THREE.Mesh(sGeo, sMat);
            sysGroup.add(starMesh);

            // Stellar Flare Halo
            const sHaloGeo = new THREE.SphereGeometry(sys.starRadius * 1.55, 24, 24);
            const sHaloMat = new THREE.MeshBasicMaterial({ color: sys.starColor, transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, side: THREE.BackSide });
            starMesh.add(new THREE.Mesh(sHaloGeo, sHaloMat));

            const sLight = new THREE.PointLight(sys.starColor, 4.0, 600);
            starMesh.add(sLight);

            // Initial position on oval orbit
            const rInit = (sys.a * (1 - sys.ecc * sys.ecc)) / (1 + sys.ecc * Math.cos(sys.angle));
            sysGroup.position.set(Math.cos(sys.angle) * rInit, 0, Math.sin(sys.angle) * rInit);

            starMesh.userData = {
                id: sys.id,
                name: sys.name,
                type: "star_system",
                sector: `Oval Orbit a=${sys.a} AU`,
                frequency: "528 Hz",
                energy_signature: "Stellar Primary",
                lore: sys.lore,
                color: sys.starColor,
                mesh: starMesh,
                sysGroup: sysGroup,
                a: sys.a,
                ecc: sys.ecc,
                angle: sys.angle,
                baseSpeed: sys.baseSpeed
            };
            stellarObjects.push(starMesh);
            sisterSystemsGroup.push(starMesh);

            // Orbiting Exoplanets for this Star
            sys.planets.forEach(p => {
                buildOvalOrbitLine(sysGroup, p.a, p.ecc, p.color);

                const epGeo = new THREE.SphereGeometry(p.radius, 24, 24);
                const epMat = new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.7 });
                const epMesh = new THREE.Mesh(epGeo, epMat);

                const epAngle = Math.random() * Math.PI * 2;
                const epR = (p.a * (1 - p.ecc * p.ecc)) / (1 + p.ecc * Math.cos(epAngle));
                epMesh.position.set(Math.cos(epAngle) * epR, 0, Math.sin(epAngle) * epR);

                epMesh.userData = {
                    id: p.name.toLowerCase().replace(/[^a-z0-9]/g, "_"),
                    name: p.name,
                    type: "exoplanet",
                    sector: sys.name,
                    frequency: "639 Hz",
                    energy_signature: "Exoplanetary Biosphere",
                    lore: p.lore,
                    color: p.color,
                    mesh: epMesh,
                    a: p.a,
                    ecc: p.ecc,
                    angle: epAngle,
                    speed: p.speed || 0.018,
                    radius: p.radius
                };
                sysGroup.add(epMesh);
                planetaryBodies.push(epMesh);
            });
        });
    }

    /* =========================================================================
       MILKY WAY GALAXY & SAGITTARIUS A* (Relativistic Fiery Plasma • NO DEAD BLACK)
       ========================================================================= */

    function createMilkyWayGalaxy(count) {
        if (milkyWayGroup) universeRoot.remove(milkyWayGroup);
        milkyWayGroup = new THREE.Group();

        // 1. Sagittarius A* (Relativistic Accretion Furnace • Fiery Molten Orange & Red Plasma)
        const bhGroup = new THREE.Group();
        bhGroup.position.set(0, 0, 0);

        // Singularity with Glowing Relativistic Burning Horizon (NO PURE BLACK)
        const bhGeo = new THREE.SphereGeometry(24, 32, 32);
        const bhMat = new THREE.MeshBasicMaterial({ color: 0x1a0500 }); // Deep molten obsidian
        const bhMesh = new THREE.Mesh(bhGeo, bhMat);
        bhGroup.add(bhMesh);

        // Blazing Fiery Accretion Disk (Molten Red-Orange-Gold Plasma with Doppler Beaming)
        const accGeo = new THREE.RingGeometry(28, 110, 64);
        const accMat = new THREE.MeshBasicMaterial({
            color: 0xff4500, // Fiery red-orange plasma
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.92,
            blending: THREE.AdditiveBlending
        });
        sgrAccretionDisk = new THREE.Mesh(accGeo, accMat);
        sgrAccretionDisk.rotation.x = Math.PI / 2.25;
        bhGroup.add(sgrAccretionDisk);

        // Blinding Golden Synchrotron Core Ring
        const synchGeo = new THREE.RingGeometry(26, 45, 64);
        const synchMat = new THREE.MeshBasicMaterial({
            color: 0xffd166,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending
        });
        const synchRing = new THREE.Mesh(synchGeo, synchMat);
        synchRing.rotation.x = Math.PI / 2.25;
        bhGroup.add(synchRing);

        // Relativistic Polar Plasma Jets (Shooting 850 units with fiery violet-cyan energy)
        const jetGeo = new THREE.CylinderGeometry(2.0, 26, 850, 16);
        const jetMat = new THREE.MeshBasicMaterial({
            color: 0x9d4edd,
            transparent: true,
            opacity: 0.55,
            blending: THREE.AdditiveBlending
        });
        sgrJetNorth = new THREE.Mesh(jetGeo, jetMat);
        sgrJetNorth.position.y = 425;
        bhGroup.add(sgrJetNorth);

        sgrJetSouth = new THREE.Mesh(jetGeo, jetMat);
        sgrJetSouth.position.y = -425;
        bhGroup.add(sgrJetSouth);

        bhMesh.userData = {
            id: "sagittarius_a",
            name: "Sagittarius A* (Supermassive Black Hole)",
            type: "supermassive_black_hole",
            sector: "Milky Way Galactic Nucleus",
            frequency: "108.50 Hz",
            energy_signature: "4-Million Solar Mass Accretion Engine",
            lore: "The central gravitational leviathan of our galaxy, encircled by a churning, boiling, molten red-orange relativistic plasma belt with relativistic synchrotron beaming.",
            color: "#ff4500",
            mesh: bhMesh
        };
        milkyWayGroup.add(bhGroup);
        stellarObjects.push(bhMesh);

        // 2. 65,000+ Spiral Arm Stars (Analytical Equations: ZERO SHAKING!)
        particlesCount = count;
        particlePositions = new Float32Array(count * 3);
        particlePhases = new Float32Array(count);
        particleRadii = new Float32Array(count);
        particleSpeeds = new Float32Array(count);
        const particleColors = new Float32Array(count * 3);

        const arms = 4;
        const starColors = [
            new THREE.Color(0x90e0ef), // Hot Blue O/B
            new THREE.Color(0xffffff), // Diamond White A
            new THREE.Color(0xffd166), // Solar Gold G
            new THREE.Color(0xf77f00), // Orange Dwarf K
            new THREE.Color(0xef4444)  // Red Giant M
        ];

        for (let i = 0; i < count; i++) {
            const armIndex = i % arms;
            const armOffset = armIndex * ((Math.PI * 2) / arms);
            const r = Math.pow(Math.random(), 0.58) * 4400 + 55;
            const spin = r * 0.0035;
            const spread = (Math.random() - 0.5) * (r * 0.18);
            const theta = armOffset + spin + (spread / r);
            const y = (Math.random() - 0.5) * (95 * Math.exp(-r / 2500));

            particleRadii[i] = r;
            particlePhases[i] = theta;
            particleSpeeds[i] = Math.sqrt(520 / (r + 100)) * 0.024; // Flat laminar rotation curve

            particlePositions[i * 3] = Math.cos(theta) * r;
            particlePositions[i * 3 + 1] = y;
            particlePositions[i * 3 + 2] = Math.sin(theta) * r;

            const sc = starColors[Math.floor(Math.random() * starColors.length)];
            particleColors[i * 3] = sc.r;
            particleColors[i * 3 + 1] = sc.g;
            particleColors[i * 3 + 2] = sc.b;
        }

        particleGeometry = new THREE.BufferGeometry();
        particleGeometry.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
        particleGeometry.setAttribute("color", new THREE.BufferAttribute(particleColors, 3));

        const starTexture = createGaussianStarTexture();
        const particleMaterial = new THREE.PointsMaterial({
            size: isMobile ? 2.2 : starSize,
            vertexColors: true,
            map: starTexture,
            transparent: true,
            opacity: 0.92,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        particleSystem = new THREE.Points(particleGeometry, particleMaterial);
        milkyWayGroup.add(particleSystem);

        // 3. 12 Massive Globular Clusters in Galactic Halo
        const globulars = [
            { id: "omega_centauri", name: "Omega Centauri (NGC 5139)", x: 2100, y: 720, z: -1400, r: 42, color: 0x90e0ef, lore: "The most massive globular cluster in the Milky Way, containing ~10 million ancient stars." },
            { id: "m13_hercules", name: "Messier 13 (Great Hercules Cluster)", x: -1800, y: 950, z: 1200, r: 35, color: 0xffd166, lore: "A dazzling sphere of several hundred thousand stars in Hercules." },
            { id: "47_tucanae", name: "47 Tucanae (NGC 104)", x: 1400, y: -1100, z: 2200, r: 38, color: 0x38ef7d, lore: "Second brightest globular cluster, hosting an extraordinarily dense stellar core." },
            { id: "m22_sagittarius", name: "Messier 22 (Sagittarius Globular)", x: 900, y: -450, z: -800, r: 32, color: 0x00f3ff, lore: "One of the nearest globular clusters to Earth, containing two confirmed stellar black holes." },
            { id: "m5_rose", name: "Messier 5 (Rose Cluster)", x: -2200, y: 800, z: -1100, r: 30, color: 0xf472b6, lore: "A 13-billion-year-old spherical cluster spanning 165 light-years." },
            { id: "m3_cluster", name: "Messier 3 (Canes Venatici Cluster)", x: -1200, y: 1350, z: 800, r: 28, color: 0xffa200, lore: "Contains roughly 500,000 stars with an unusually high proportion of variable stars." },
            { id: "m15_pegasus", name: "Messier 15 (Pegasus Globular)", x: 2600, y: 650, z: 1800, r: 29, color: 0xa855f7, lore: "Underwent core collapse; suspected to harbor an intermediate-mass black hole." },
            { id: "m92_hercules", name: "Messier 92", x: -900, y: 1150, z: 1900, r: 26, color: 0x38bdf8, lore: "One of the oldest surviving clusters in the Milky Way, over 14 billion years old." },
            { id: "m4_scorpius", name: "Messier 4 (Scorpius Cluster)", x: 1100, y: -300, z: -1600, r: 27, color: 0xfacc15, lore: "The closest globular cluster to our solar system, located in Scorpius." },
            { id: "m2_aquarius", name: "Messier 2", x: 2400, y: -850, z: 700, r: 28, color: 0x67e8f9, lore: "A rich, compact globular cluster composed of 150,000 stars." },
            { id: "ngc_6397", name: "NGC 6397 (Ara Globular)", x: 600, y: -900, z: -2100, r: 25, color: 0x34d399, lore: "A collapsed-core cluster with thousands of white dwarf stellar remnants." },
            { id: "palomar_5", name: "Palomar 5 (Tidal Stream Cluster)", x: -3100, y: 1500, z: -600, r: 24, color: 0xe879f9, lore: "A disrupting globular cluster exhibiting massive stellar tidal streams stretching across the halo." }
        ];

        globulars.forEach(gc => {
            const gcGroup = new THREE.Group();
            gcGroup.position.set(gc.x, gc.y, gc.z);

            const coreGeo = new THREE.SphereGeometry(gc.r * 0.35, 16, 16);
            const coreMat = new THREE.MeshBasicMaterial({ color: gc.color, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending });
            const coreMesh = new THREE.Mesh(coreGeo, coreMat);
            gcGroup.add(coreMesh);

            const gcCount = 650;
            const gcPos = new Float32Array(gcCount * 3);
            for (let i = 0; i < gcCount; i++) {
                const gr = Math.pow(Math.random(), 0.45) * gc.r;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(Math.random() * 2 - 1);
                gcPos[i * 3] = gr * Math.sin(phi) * Math.cos(theta);
                gcPos[i * 3 + 1] = gr * Math.sin(phi) * Math.sin(theta);
                gcPos[i * 3 + 2] = gr * Math.cos(phi);
            }
            const gcGeo = new THREE.BufferGeometry();
            gcGeo.setAttribute("position", new THREE.BufferAttribute(gcPos, 3));
            const gcPointsMat = new THREE.PointsMaterial({
                size: 2.0,
                color: gc.color,
                transparent: true,
                opacity: 0.78,
                blending: THREE.AdditiveBlending,
                map: starTexture,
                depthWrite: false
            });
            gcGroup.add(new THREE.Points(gcGeo, gcPointsMat));

            coreMesh.userData = {
                id: gc.id,
                name: gc.name,
                type: "globular_cluster",
                sector: "Milky Way Halo",
                frequency: "528.00 Hz",
                energy_signature: "Ancient Gravitational Halo Swarm",
                lore: gc.lore,
                color: "#" + gc.color.toString(16).padStart(6, "0"),
                mesh: coreMesh
            };
            milkyWayGroup.add(gcGroup);
            stellarObjects.push(coreMesh);
        });

        // 4. 8 Rich Open Clusters in the Galactic Disk
        const openClusters = [
            { id: "pleiades_m45", name: "Pleiades (Seven Sisters / M45)", x: 2750, y: 35, z: 1780, r: 35, color: 0x00f3ff, lore: "A famous open cluster enveloped in brilliant blue reflection nebulosity in Taurus." },
            { id: "hyades_cluster", name: "Hyades Moving Group", x: 2650, y: 20, z: 1950, r: 30, color: 0xffd166, lore: "The closest open cluster to our Sun, forming the V-shaped head of Taurus." },
            { id: "m11_wild_duck", name: "Wild Duck Cluster (M11)", x: 1950, y: -15, z: 850, r: 28, color: 0x38ef7d, lore: "One of the most densely populated and massive open star clusters known." },
            { id: "m6_butterfly", name: "Butterfly Cluster (M6)", x: 1450, y: -25, z: -600, r: 25, color: 0xf472b6, lore: "A picturesque star cluster in Scorpius whose stars trace the wings of a butterfly." },
            { id: "m44_beehive", name: "Beehive Cluster (Praesepe / M44)", x: 2400, y: 45, z: 1350, r: 32, color: 0x38bdf8, lore: "An open cluster in Cancer visible to the naked eye since classical antiquity." },
            { id: "m7_ptolemy", name: "Ptolemy Cluster (M7)", x: 1200, y: -30, z: -950, r: 26, color: 0xa855f7, lore: "A brilliant open cluster near the tail of the scorpion recorded by Ptolemy in 130 AD." },
            { id: "ngc_4755_jewel", name: "Jewel Box Cluster (NGC 4755)", x: 1750, y: -10, z: 2400, r: 24, color: 0xec4899, lore: "A glittering gemstone cluster of blue, ruby, and golden supergiant stars." },
            { id: "double_cluster", name: "Double Cluster (h & Chi Persei)", x: 3300, y: 50, z: 2200, r: 36, color: 0xffa200, lore: "Twin massive open star clusters shining side-by-side in Perseus." }
        ];

        openClusters.forEach(oc => {
            const ocGroup = new THREE.Group();
            ocGroup.position.set(oc.x, oc.y, oc.z);

            const ocCoreGeo = new THREE.SphereGeometry(oc.r * 0.28, 14, 14);
            const ocCoreMat = new THREE.MeshBasicMaterial({ color: oc.color, transparent: true, opacity: 0.82, blending: THREE.AdditiveBlending });
            const ocCore = new THREE.Mesh(ocCoreGeo, ocCoreMat);
            ocGroup.add(ocCore);

            const ocCount = 380;
            const ocPos = new Float32Array(ocCount * 3);
            for (let i = 0; i < ocCount; i++) {
                const or_ = Math.random() * oc.r;
                const theta = Math.random() * Math.PI * 2;
                ocPos[i * 3] = Math.cos(theta) * or_;
                ocPos[i * 3 + 1] = (Math.random() - 0.5) * (oc.r * 0.35);
                ocPos[i * 3 + 2] = Math.sin(theta) * or_;
            }
            const ocGeo = new THREE.BufferGeometry();
            ocGeo.setAttribute("position", new THREE.BufferAttribute(ocPos, 3));
            const ocMat = new THREE.PointsMaterial({
                size: 2.2,
                color: oc.color,
                transparent: true,
                opacity: 0.85,
                blending: THREE.AdditiveBlending,
                map: starTexture,
                depthWrite: false
            });
            ocGroup.add(new THREE.Points(ocGeo, ocMat));

            ocCore.userData = {
                id: oc.id,
                name: oc.name,
                type: "open_cluster",
                sector: "Milky Way Disk",
                frequency: "639.00 Hz",
                energy_signature: "Stellar Nursery Open Swarm",
                lore: oc.lore,
                color: "#" + oc.color.toString(16).padStart(6, "0"),
                mesh: ocCore
            };
            milkyWayGroup.add(ocGroup);
            stellarObjects.push(ocCore);
        });

        universeRoot.add(milkyWayGroup);

        if (microParticles) microParticles.innerText = count.toLocaleString() + " Stars";
    }

    /* =========================================================================
       SCALE 5: LANIAKEA MEGA-CLUSTER & THE GREAT ATTRACTOR
       ========================================================================= */

    function createSuperclusterScale() {
        superclusterGroup = new THREE.Group();

        // 1. The Great Attractor (Gravitational Nexus)
        const gaGeo = new THREE.SphereGeometry(520, 32, 32);
        const gaMat = new THREE.MeshBasicMaterial({ color: 0xff0055, transparent: true, opacity: 0.92, blending: THREE.AdditiveBlending });
        const gaMesh = new THREE.Mesh(gaGeo, gaMat);
        gaMesh.position.set(52000, 11000, -42000);

        // Radiant Synchrotron Gravitational Aura
        const gaAuraGeo = new THREE.SphereGeometry(950, 24, 24);
        const gaAuraMat = new THREE.MeshBasicMaterial({ color: 0xff007f, transparent: true, opacity: 0.28, blending: THREE.AdditiveBlending, side: THREE.BackSide });
        gaMesh.add(new THREE.Mesh(gaAuraGeo, gaAuraMat));

        gaMesh.userData = {
            id: "great_attractor",
            name: "The Great Attractor (Gravitational Nexus)",
            type: "cosmic_nexus",
            sector: "Laniakea Zone of Avoidance",
            frequency: "396.00 Hz",
            energy_signature: "Colossal Gravitational Infall Sink",
            lore: "A titanic gravitational anomaly pulling hundreds of thousands of galaxies along luminous velocity streamlines.",
            color: "#ff0055",
            mesh: gaMesh
        };
        superclusterGroup.add(gaMesh);
        stellarObjects.push(gaMesh);

        // 2. 16 Major Galaxy Clusters (Comprising 450+ Orbiting Galaxies)
        const clusters = [
            { id: "virgo_cluster", name: "Virgo Cluster (Messier 87 Core)", x: 32000, y: 8800, z: 26000, color: 0x38ef7d, radius: 4200, count: 35, lore: "Heart of the Virgo Supercluster, anchored by the giant elliptical galaxy M87." },
            { id: "coma_cluster", name: "Coma Cluster (Abell 1656 • NGC 4889)", x: 58000, y: 24000, z: 18000, color: 0x60a5fa, radius: 5200, count: 32, lore: "A dense swarm containing over 1,000 galaxies, dominated by two supergiant ellipticals." },
            { id: "perseus_cluster", name: "Perseus Cluster (Abell 426 • NGC 1275)", x: -45000, y: 16000, z: -38000, color: 0xa855f7, radius: 4800, count: 30, lore: "The brightest X-ray cluster in the sky, pulsing with acoustic gravity sound waves." },
            { id: "centaurus_cluster", name: "Centaurus Cluster (Abell 3526)", x: -28000, y: 6400, z: -22000, color: 0xffa200, radius: 3800, count: 28, lore: "A rich galaxy cluster engaged in complex gravitational substructure merger." },
            { id: "hydra_cluster", name: "Hydra Cluster (Abell 1060)", x: -38000, y: -18000, z: 29000, color: 0x38bdf8, radius: 4100, count: 26, lore: "Dominated by the diffuse cD galaxy NGC 3311 with a rich halo of globular systems." },
            { id: "fornax_cluster", name: "Fornax Cluster (NGC 1399 & 1365)", x: -42000, y: -14000, z: 42000, color: 0xf97316, radius: 3600, count: 28, lore: "A compact nearby cluster featuring the spectacular barred spiral NGC 1365." },
            { id: "norma_cluster", name: "Norma Cluster (Abell 3627 Nexus)", x: 51000, y: 10500, z: -41000, color: 0xff0055, radius: 5800, count: 36, lore: "Residing in the heart of the Great Attractor, drawing mass from across Laniakea." },
            { id: "antlia_cluster", name: "Antlia Cluster (NGC 3268)", x: -22000, y: -19000, z: -15000, color: 0x2dd4bf, radius: 3200, count: 24, lore: "A rare double-nucleated cluster divided between subgroups NGC 3268 and NGC 3258." },
            { id: "shapley_cluster", name: "Shapley Supercluster Core (IC 1101)", x: 85000, y: 36000, z: -65000, color: 0xe0e7ff, radius: 7500, count: 40, lore: "The largest mass concentration in the observable universe, anchored by IC 1101." },
            { id: "hercules_cluster", name: "Hercules Cluster (Abell 2151)", x: 48000, y: 31000, z: 44000, color: 0xec4899, radius: 4600, count: 30, lore: "A young, spiral-rich cluster brimming with gas-rich interacting and colliding galaxies." },
            { id: "leo_cluster", name: "Leo Cluster (Abell 1367)", x: 36000, y: 22000, z: -28000, color: 0xfacc15, radius: 3900, count: 26, lore: "A dynamic cluster connected to the Coma Cluster via a long cosmological filament." },
            { id: "ursa_major_cluster", name: "Ursa Major Cluster (NGC 3992)", x: -32000, y: 28000, z: -19000, color: 0x00d4ff, radius: 3700, count: 25, lore: "A loose, spiral-dominated galaxy concentration lacking a single giant central elliptical." },
            { id: "local_group_swarm", name: "Local Group Outskirts (M31 Andromeda)", x: 14000, y: 2800, z: -11000, color: 0x00f3ff, radius: 3100, count: 24, lore: "Our galactic neighborhood, anchored by Andromeda M31, Triangulum M33, and Magellanic clouds." },
            { id: "m81_group", name: "M81 Group (Bode & Cigar Galaxies)", x: -27000, y: 16000, z: -14000, color: 0x67e8f9, radius: 2800, count: 22, lore: "A picturesque interacting galaxy group featuring starburst galaxy M82." },
            { id: "sculptor_group", name: "Sculptor Group (NGC 253 Silver Coin)", x: 21000, y: -18000, z: -19000, color: 0xe2e8f0, radius: 2900, count: 22, lore: "One of the closest galaxy groups to the Local Group, centered on starburst NGC 253." },
            { id: "canes_venatici_cloud", name: "Canes Venatici Cloud (Whirlpool M51)", x: -19000, y: 12000, z: 18000, color: 0xa855f7, radius: 3400, count: 25, lore: "A sprawling filamentary group of magnificent spiral galaxies led by M51." }
        ];

        clusters.forEach(cl => {
            const clGroup = new THREE.Group();
            clGroup.position.set(cl.x, cl.y, cl.z);

            // Cluster Central Dominant Galaxy Bulge
            const cBulgeGeo = new THREE.SphereGeometry(cl.radius * 0.16, 20, 20);
            const cBulgeMat = new THREE.MeshBasicMaterial({ color: cl.color, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending });
            const cBulge = new THREE.Mesh(cBulgeGeo, cBulgeMat);
            clGroup.add(cBulge);

            // Orbiting Satellite Galaxies in this Cluster
            for (let g = 0; g < cl.count; g++) {
                const gr = (cl.radius * 0.22) + Math.random() * (cl.radius * 0.78);
                const gTheta = (g / cl.count) * Math.PI * 2 + Math.random() * 0.4;
                const gx = Math.cos(gTheta) * gr;
                const gy = (Math.random() - 0.5) * (cl.radius * 0.25);
                const gz = Math.sin(gTheta) * gr;

                const satGeo = new THREE.SphereGeometry(14 + Math.random() * 22, 12, 12);
                const satMat = new THREE.MeshBasicMaterial({ color: cl.color, transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending });
                const satMesh = new THREE.Mesh(satGeo, satMat);
                satMesh.position.set(gx, gy, gz);
                clGroup.add(satMesh);
            }

            // Cluster Galactic Gas & Micro-Starlight Swarm
            const starCount = 650;
            const pos = new Float32Array(starCount * 3);
            for (let i = 0; i < starCount; i++) {
                const r = Math.random() * cl.radius;
                const theta = Math.random() * Math.PI * 2 + (r * 0.008);
                pos[i * 3] = Math.cos(theta) * r;
                pos[i * 3 + 1] = (Math.random() - 0.5) * (r * 0.2);
                pos[i * 3 + 2] = Math.sin(theta) * r;
            }
            const gGeo = new THREE.BufferGeometry();
            gGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
            const gMat = new THREE.PointsMaterial({
                size: 2.4,
                color: cl.color,
                transparent: true,
                opacity: 0.75,
                blending: THREE.AdditiveBlending,
                map: createGaussianStarTexture(),
                depthWrite: false
            });
            clGroup.add(new THREE.Points(gGeo, gMat));

            cBulge.userData = {
                id: cl.id,
                name: cl.name,
                type: "galaxy_cluster",
                sector: "Laniakea Supercluster",
                frequency: "285.00 Hz",
                energy_signature: `${cl.count} Member Galaxies Swarm`,
                lore: cl.lore,
                color: "#" + cl.color.toString(16).padStart(6, "0"),
                mesh: cBulge
            };
            superclusterGroup.add(clGroup);
            stellarObjects.push(cBulge);
        });

        // 3. 6,000 Deep-Field Background Galaxies (Hubble/JWST Ultra Deep Field Sky Shell)
        const deepFieldCount = 6000;
        const dfPositions = new Float32Array(deepFieldCount * 3);
        const dfColors = new Float32Array(deepFieldCount * 3);
        const dfPalette = [
            new THREE.Color(0x90e0ef),
            new THREE.Color(0xffffff),
            new THREE.Color(0xffd166),
            new THREE.Color(0xf472b6),
            new THREE.Color(0x38ef7d),
            new THREE.Color(0xa855f7)
        ];

        for (let i = 0; i < deepFieldCount; i++) {
            const r = 38000 + Math.pow(Math.random(), 0.5) * 190000;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(Math.random() * 2 - 1);

            dfPositions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            dfPositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            dfPositions[i * 3 + 2] = r * Math.cos(phi);

            const c = dfPalette[Math.floor(Math.random() * dfPalette.length)];
            dfColors[i * 3] = c.r;
            dfColors[i * 3 + 1] = c.g;
            dfColors[i * 3 + 2] = c.b;
        }

        const dfGeo = new THREE.BufferGeometry();
        dfGeo.setAttribute("position", new THREE.BufferAttribute(dfPositions, 3));
        dfGeo.setAttribute("color", new THREE.BufferAttribute(dfColors, 3));

        const dfMat = new THREE.PointsMaterial({
            size: 2.8,
            vertexColors: true,
            map: createGaussianStarTexture(),
            transparent: true,
            opacity: 0.78,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        superclusterGroup.add(new THREE.Points(dfGeo, dfMat));

        universeRoot.add(superclusterGroup);
    }

    /* =========================================================================
       SCALE 6: OBSERVABLE COSMIC WEB & BOÖTES SUPERVOID (36 NODES • 8,000 FILAMENTS)
       ========================================================================= */

    function createCosmicWebScale() {
        cosmicWebGroup = new THREE.Group();

        // 36 Major Cosmic Macro Nodes spanning across 600,000 units
        const webNodes = [
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(52000, 11000, -42000),
            new THREE.Vector3(-65000, 32000, -50000),
            new THREE.Vector3(75000, -35000, 62000),
            new THREE.Vector3(-85000, -42000, 78000),
            new THREE.Vector3(95000, 55000, -85000),
            new THREE.Vector3(-110000, 48000, 92000),
            new THREE.Vector3(135000, -62000, -115000),
            new THREE.Vector3(-145000, -75000, -125000),
            new THREE.Vector3(160000, 82000, 130000),
            new THREE.Vector3(-175000, 88000, -140000),
            new THREE.Vector3(190000, -95000, 155000),
            new THREE.Vector3(-205000, -105000, 168000),
            new THREE.Vector3(220000, 115000, -182000),
            new THREE.Vector3(-235000, 125000, 195000),
            new THREE.Vector3(250000, -135000, -210000),
            new THREE.Vector3(-265000, -145000, -225000),
            new THREE.Vector3(280000, 155000, 240000),
            new THREE.Vector3(-295000, 165000, -255000),
            new THREE.Vector3(310000, -175000, 270000),
            new THREE.Vector3(-325000, -185000, 285000),
            new THREE.Vector3(340000, 195000, -300000),
            new THREE.Vector3(-355000, 205000, 315000),
            new THREE.Vector3(370000, -215000, -330000),
            new THREE.Vector3(-385000, -225000, -345000),
            new THREE.Vector3(400000, 235000, 360000),
            new THREE.Vector3(-415000, 245000, -375000),
            new THREE.Vector3(430000, -255000, 390000),
            new THREE.Vector3(-445000, -265000, 405000),
            new THREE.Vector3(460000, 275000, -420000),
            new THREE.Vector3(-475000, 285000, 435000),
            new THREE.Vector3(490000, -295000, -450000),
            new THREE.Vector3(-505000, -305000, -465000),
            new THREE.Vector3(520000, 315000, 480000),
            new THREE.Vector3(-535000, 325000, -495000),
            new THREE.Vector3(550000, -335000, 510000)
        ];

        // Luminous Dark-Matter Filament Bridges (connecting k-nearest neighbors)
        const lineMat = new THREE.LineBasicMaterial({ color: 0x9d4edd, transparent: true, opacity: 0.32, blending: THREE.AdditiveBlending });

        for (let i = 0; i < webNodes.length; i++) {
            // Connect to nearest 4 neighbors
            const dists = [];
            for (let j = 0; j < webNodes.length; j++) {
                if (i !== j) {
                    dists.push({ j, d: webNodes[i].distanceTo(webNodes[j]) });
                }
            }
            dists.sort((a, b) => a.d - b.d);
            for (let k = 0; k < Math.min(4, dists.length); k++) {
                const j = dists[k].j;
                if (i < j) {
                    const pts = [webNodes[i], webNodes[j]];
                    const lGeo = new THREE.BufferGeometry().setFromPoints(pts);
                    cosmicWebGroup.add(new THREE.Line(lGeo, lineMat));
                }
            }
        }

        // 8,000 Filament Dark-Matter Flow Particles
        const filCount = 8000;
        const filPos = new Float32Array(filCount * 3);
        for (let i = 0; i < filCount; i++) {
            const nIdx = Math.floor(Math.random() * webNodes.length);
            const nNext = (nIdx + 1 + Math.floor(Math.random() * 3)) % webNodes.length;
            const alpha = Math.random();
            const p = new THREE.Vector3().lerpVectors(webNodes[nIdx], webNodes[nNext], alpha);
            p.x += (Math.random() - 0.5) * 4500;
            p.y += (Math.random() - 0.5) * 4500;
            p.z += (Math.random() - 0.5) * 4500;
            filPos[i * 3] = p.x;
            filPos[i * 3 + 1] = p.y;
            filPos[i * 3 + 2] = p.z;
        }
        const filGeo = new THREE.BufferGeometry();
        filGeo.setAttribute("position", new THREE.BufferAttribute(filPos, 3));
        const filMat = new THREE.PointsMaterial({
            size: 2.2,
            color: 0xc084fc,
            transparent: true,
            opacity: 0.65,
            blending: THREE.AdditiveBlending,
            map: createGaussianStarTexture(),
            depthWrite: false
        });
        cosmicWebGroup.add(new THREE.Points(filGeo, filMat));

        // Boötes Supervoid (The Great Nothingness)
        const bvGeo = new THREE.SphereGeometry(38000, 24, 24);
        const bvMat = new THREE.MeshBasicMaterial({ color: 0x050515, transparent: true, opacity: 0.12, side: THREE.BackSide });
        const bvMesh = new THREE.Mesh(bvGeo, bvMat);
        bvMesh.position.set(120000, 40000, -90000);
        bvMesh.userData = {
            id: "bootes_supervoid",
            name: "Boötes Supervoid (The Great Nothing)",
            type: "supervoid",
            sector: "Abyssal Observable Void",
            frequency: "174.00 Hz",
            energy_signature: "Ultra-Low Density Dark Energy Domain",
            lore: "An immense spherical void spanning nearly 330 million light-years, containing almost no galaxies.",
            color: "#6366f1",
            mesh: bvMesh
        };
        cosmicWebGroup.add(bvMesh);
        stellarObjects.push(bvMesh);

        // Eridanus Supervoid (CMB Cold Spot Origin)
        const evGeo = new THREE.SphereGeometry(45000, 24, 24);
        const evMat = new THREE.MeshBasicMaterial({ color: 0x030712, transparent: true, opacity: 0.12, side: THREE.BackSide });
        const evMesh = new THREE.Mesh(evGeo, evMat);
        evMesh.position.set(-130000, -60000, 110000);
        evMesh.userData = {
            id: "eridanus_supervoid",
            name: "Eridanus Supervoid (CMB Cold Spot)",
            type: "supervoid",
            sector: "Primordial Inflation Dip",
            frequency: "144.00 Hz",
            energy_signature: "Cosmic Microwave Background Anomaly",
            lore: "A colossal cold void theorized to be quantum entanglement with an adjacent bubble universe.",
            color: "#38bdf8",
            mesh: evMesh
        };
        cosmicWebGroup.add(evMesh);
        stellarObjects.push(evMesh);

        universeRoot.add(cosmicWebGroup);
    }

    /* =========================================================================
       SCALE 7: BUBBLE MULTIVERSE & QUANTUM DOMAINS (NO BOXES! Hyperspherical Bubbles)
       ========================================================================= */

    function createBubbleMultiverseScale() {
        bubbleMultiverseGroup = new THREE.Group();
        bubbleUniverses = [];

        // 6 Hyperspherical Bubble Universes in the Quantum Inflaton Void (NO BOXES!)
        // Each external universe contains a complete living galaxy, central supermassive engine, and explorable alien solar systems!
        const bubbleConfigs = [
            { 
                id: "prime_cosmos", 
                name: "Prime Observable Bubble Universe", 
                x: 0, y: 0, z: 0, radius: 28000, color: 0x00f3ff, 
                lore: "Our home universe: expanding under fine-tuned dark energy and inflationary spacetime laws." 
            },
            { 
                id: "antimatter_cosmos", 
                name: "Antimatter Symmetrical Domain", 
                x: 75000, y: 28000, z: -65000, radius: 24000, color: 0xff007f, 
                coreName: "Lux Obscura (Supermassive White Hole)",
                lore: "A parallel universe where baryogenesis favored antiprotons and positrons, lit by white hole radiation.",
                systems: [
                    { name: "Positron Prime (Crystalline Star)", a: 5200, ecc: 0.08, r: 120, color: "#f43f5e", planets: [{ name: "Caelum-Anti (Crystal Terrestrial)", a: 380, ecc: 0.04, r: 18, color: "#fb7185", lore: "A world of crystal spires bathed in antimatter luminescence." }, { name: "Vitreus (Prismatic Gas World)", a: 720, ecc: 0.09, r: 35, color: "#f472b6", lore: "A giant world of refracting glass clouds." }] },
                    { name: "Dirac Sanctuary (Violet Dwarf)", a: 9800, ecc: 0.12, r: 95, color: "#d946ef", planets: [{ name: "Dirac-b (Mirror Habitable)", a: 420, ecc: 0.05, r: 22, color: "#e879f9", lore: "A habitable world obeying inverted chiral symmetry." }] },
                    { name: "C-Symmetry Cradle", a: 15400, ecc: 0.16, r: 110, color: "#ec4899", planets: [{ name: "Symmetry-1 (Basalt Mirror)", a: 550, ecc: 0.07, r: 20, color: "#f43f5e", lore: "A dense metallic world orbiting at high velocity." }] }
                ]
            },
            { 
                id: "supersymmetric_cosmos", 
                name: "Supersymmetric Chronos Realm", 
                x: -82000, y: -35000, z: 72000, radius: 26000, color: 0x9d4edd, 
                coreName: "Chronos Nexus (Graviton Singularity)",
                lore: "A realm of unbroken supersymmetry where quantum gravitons stabilize spacetime and halt entropy.",
                systems: [
                    { name: "Tachyon Prime (Luminescent Star)", a: 5600, ecc: 0.09, r: 130, color: "#a855f7", planets: [{ name: "Chronos-T1 (Temporal Eden)", a: 420, ecc: 0.03, r: 24, color: "#38ef7d", lore: "A paradise where biological aging is arrested by graviton resonance." }, { name: "Aeon-Flow (Supersymmetric Jovian)", a: 810, ecc: 0.08, r: 38, color: "#c084fc", lore: "A Jovian world with iridescent plasma rings." }] },
                    { name: "Graviton Nexus Star", a: 10500, ecc: 0.14, r: 105, color: "#8b5cf6", planets: [{ name: "Graviton-Alpha", a: 460, ecc: 0.06, r: 21, color: "#a78bfa", lore: "A high-density super-Earth with extreme surface gravity." }] },
                    { name: "Aeon Cradle (Pulsating Star)", a: 16800, ecc: 0.18, r: 115, color: "#7c3aed", planets: [{ name: "Quantum-Eden", a: 620, ecc: 0.05, r: 25, color: "#34d399", lore: "A lush biosphere harboring exotic quantum organisms." }] }
                ]
            },
            { 
                id: "cryogenic_void_cosmos", 
                name: "Cryogenic Dark Energy Sphere", 
                x: 95000, y: -45000, z: 88000, radius: 32000, color: 0x38ef7d, 
                coreName: "Absolute Zero Singular Core",
                lore: "A deep freeze universe where dark energy accelerated expansion into pristine, crystalline vacuum.",
                systems: [
                    { name: "Niflheim Prime (Sub-Zero Star)", a: 6400, ecc: 0.07, r: 125, color: "#2dd4bf", planets: [{ name: "Niflheim-b (Frozen Ocean Haven)", a: 480, ecc: 0.04, r: 22, color: "#06b6d4", lore: "An icy world with liquid subsurface oceans warmed by tidal friction." }, { name: "Ymir-Ice (Diamond Methane World)", a: 890, ecc: 0.08, r: 34, color: "#67e8f9", lore: "A world where liquid methane rains over diamond mountains." }] },
                    { name: "Glacies Major (Frost Giant Star)", a: 12200, ecc: 0.11, r: 110, color: "#14b8a6", planets: [{ name: "Frost-Giant Sovereign", a: 540, ecc: 0.06, r: 36, color: "#5eead4", lore: "A massive ice giant surrounded by 64 captured cryo-moons." }] },
                    { name: "Zero-Kelvin Cradle", a: 19500, ecc: 0.15, r: 100, color: "#0d9488", planets: [{ name: "Cryo-Haven", a: 680, ecc: 0.05, r: 23, color: "#a7f3d0", lore: "A serene biosphere sustained by geothermal mantle plumes." }] }
                ]
            },
            { 
                id: "high_entropy_cosmos", 
                name: "High-Entropy Plasma Domain", 
                x: -98000, y: 52000, z: -85000, radius: 25000, color: 0xffd166, 
                coreName: "Sol Invictus Maximus (Hyper-Magnetar)",
                lore: "An energetic cosmos where stellar nucleosynthesis never ceased, blazing with golden thermonuclear plasma.",
                systems: [
                    { name: "Vulcan Prime (Thermonuclear Star)", a: 5400, ecc: 0.08, r: 135, color: "#f59e0b", planets: [{ name: "Vulcan-b (Molten Gold Terrestrial)", a: 410, ecc: 0.04, r: 22, color: "#fbbf24", lore: "A planet of liquid gold oceans and incandescent basalt continents." }, { name: "Corona-Max (Hot Plasma Jovian)", a: 780, ecc: 0.09, r: 40, color: "#f97316", lore: "A gas giant radiating intense golden heat." }] },
                    { name: "Helios Invictus (Golden Binary)", a: 10400, ecc: 0.13, r: 115, color: "#d97706", planets: [{ name: "Aureus (Super-Earth Eden)", a: 510, ecc: 0.05, r: 26, color: "#fde047", lore: "A world of solar towers and golden photosynthetic vegetation." }] },
                    { name: "Prometheus Flare Star", a: 16200, ecc: 0.17, r: 120, color: "#ea580c", planets: [{ name: "Pyros (Magma Sanctuary)", a: 640, ecc: 0.07, r: 24, color: "#ef4444", lore: "A fortress world shielded by colossal planetary magnetic fields." }] }
                ]
            },
            { 
                id: "compactified_bulk_cosmos", 
                name: "11-Dimensional M-Theory Sphere", 
                x: 0, y: 110000, z: 0, radius: 35000, color: 0x00d4ff, 
                coreName: "Calabi-Yau 11D Singularity",
                lore: "A higher-dimensional bulk domain with seven compactified Calabi-Yau manifolds shaping physical constants.",
                systems: [
                    { name: "Brane-11 Prime (Quantum Hyper-Star)", a: 7200, ecc: 0.07, r: 140, color: "#38bdf8", planets: [{ name: "String-1 (Higher Dimensional World)", a: 520, ecc: 0.03, r: 25, color: "#0ea5e9", lore: "A world where macroscopic quantum superposition is directly observable." }, { name: "Vibration-Alpha", a: 950, ecc: 0.08, r: 38, color: "#7dd3fc", lore: "A pearlescent gas giant humming with superstring vibrations." }] },
                    { name: "Superstring Nexus Star", a: 13800, ecc: 0.12, r: 120, color: "#0284c7", planets: [{ name: "Manifold-Eden", a: 620, ecc: 0.05, r: 27, color: "#38ef7d", lore: "A crystalline world with geometry folded into Calabi-Yau symmetries." }] },
                    { name: "Holomorphic Cradle", a: 22000, ecc: 0.16, r: 110, color: "#0369a1", planets: [{ name: "Topology-Prime", a: 750, ecc: 0.06, r: 23, color: "#67e8f9", lore: "A planet governed by topological quantum field dynamics." }] }
                ]
            }
        ];

        // 42 Procedurally Generated Exotic Bubble Universes stretching to 1,500,000 units
        const exoticThemes = [
            { prefix: "Quintessence", name: "Dynamic Dark Energy Crucible", color: 0x38ef7d, lore: "Spacetime ruled by rolling quintessence scalar fields." },
            { prefix: "AdS Hologram", name: "Anti-de Sitter Conformal Sphere", color: 0x00f3ff, lore: "A negative cosmological constant domain encoding 4D gravity on a conformal boundary." },
            { prefix: "Variable-c", name: "Superluminal Velocity Matrix", color: 0xffa200, lore: "The speed of light varies spatially, warping causal light cones." },
            { prefix: "Baryon-Zero", name: "Pure Photonic Condensate", color: 0xffd166, lore: "Matter failed to condense; an ocean of pure electromagnetic standing waves." },
            { prefix: "Tachyonic", name: "Inverted Causality Bubble", color: 0xec4899, lore: "Superluminal particles dominate; entropy flows inversely along the arrow of time." },
            { prefix: "Chrono-Synclastic", name: "Temporal Infundibulum", color: 0xa855f7, lore: "All paradoxes and timeline branches coexist in harmonic superposition." },
            { prefix: "Fuzzy Cold Dark Matter", name: "Ultralight Axion Superfluid", color: 0x67e8f9, lore: "Giant quantum galactic cores formed of Bose-Einstein condensates." }
        ];

        for (let i = 1; i <= 42; i++) {
            const theme = exoticThemes[i % exoticThemes.length];
            const dist = 160000 + Math.pow(i / 42, 0.75) * 1340000;
            const theta = (i * 2.39996) % (Math.PI * 2);
            const phi = Math.acos(1 - (2 * (i + 0.5)) / 43);

            const bx = dist * Math.sin(phi) * Math.cos(theta);
            const by = dist * Math.sin(phi) * Math.sin(theta);
            const bz = dist * Math.cos(phi);
            const br = 28000 + (i % 5) * 8000;

            bubbleConfigs.push({
                id: `multiverse_domain_${i}`,
                name: `${theme.prefix} Domain Omega-${i}`,
                x: bx,
                y: by,
                z: bz,
                radius: br,
                color: theme.color,
                coreName: `${theme.prefix} Hyper-Core`,
                lore: theme.lore,
                systems: [
                    {
                        name: `${theme.prefix} Prime Star`,
                        a: br * 0.22,
                        ecc: 0.08,
                        r: 110,
                        color: "#" + theme.color.toString(16).padStart(6, "0"),
                        planets: [
                            { name: `${theme.prefix}-World Alpha`, a: 450, ecc: 0.04, r: 22, color: "#" + theme.color.toString(16).padStart(6, "0"), lore: "An alien world cradled by exotic cosmological laws." }
                        ]
                    }
                ]
            });
        }

        bubbleConfigs.forEach(b => {
            const bGroup = new THREE.Group();
            bGroup.position.set(b.x, b.y, b.z);

            // Shimmering Iridescent Hyperspherical Boundary
            const bGeo = new THREE.SphereGeometry(b.radius, 32, 32);
            const bMat = new THREE.MeshBasicMaterial({
                color: b.color,
                transparent: true,
                opacity: 0.16,
                blending: THREE.AdditiveBlending,
                side: THREE.BackSide
            });
            const bMesh = new THREE.Mesh(bGeo, bMat);
            bGroup.add(bMesh);

            // If it's an external bubble universe, instantiate its central supermassive engine & living systems!
            if (b.id !== "prime_cosmos") {
                // 1. Central Supermassive Engine
                const coreGeo = new THREE.SphereGeometry(b.radius * 0.065, 24, 24);
                const coreMat = new THREE.MeshBasicMaterial({
                    color: b.color,
                    transparent: true,
                    opacity: 0.85,
                    blending: THREE.AdditiveBlending
                });
                const core = new THREE.Mesh(coreGeo, coreMat);
                bGroup.add(core);

                // Fiery Accretion Torus around the Core
                const ringGeo = new THREE.RingGeometry(b.radius * 0.08, b.radius * 0.22, 48);
                const ringMat = new THREE.MeshBasicMaterial({
                    color: b.color,
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.5,
                    blending: THREE.AdditiveBlending
                });
                const ringMesh = new THREE.Mesh(ringGeo, ringMat);
                ringMesh.rotation.x = Math.PI / 2.2;
                core.add(ringMesh);

                core.userData = {
                    id: b.id,
                    name: `${b.name} • ${b.coreName}`,
                    type: "bubble_universe",
                    sector: "Quantum Inflaton Void",
                    frequency: "963.00 Hz",
                    energy_signature: "Hyperspherical Spacetime Domain",
                    lore: b.lore,
                    color: "#" + b.color.toString(16).padStart(6, "0"),
                    mesh: core,
                    radius: b.radius
                };
                bubbleUniverses.push(core);
                stellarObjects.push(core);

                // 2. Swirling Internal Galaxy Spiral (2,000 Glowing Stars)
                const starCount = 2000;
                const pos = new Float32Array(starCount * 3);
                for (let i = 0; i < starCount; i++) {
                    const r = Math.random() * b.radius * 0.82;
                    const theta = Math.random() * Math.PI * 2 + (r * 0.001);
                    pos[i * 3] = Math.cos(theta) * r;
                    pos[i * 3 + 1] = (Math.random() - 0.5) * (r * 0.15);
                    pos[i * 3 + 2] = Math.sin(theta) * r;
                }
                const starsGeo = new THREE.BufferGeometry();
                starsGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
                const starsMat = new THREE.PointsMaterial({
                    size: 4.2,
                    color: b.color,
                    transparent: true,
                    opacity: 0.75,
                    blending: THREE.AdditiveBlending,
                    map: createGaussianStarTexture(),
                    depthWrite: false
                });
                bGroup.add(new THREE.Points(starsGeo, starsMat));

                // 3. Complete Explorable Alien Solar Systems inside this Bubble Universe
                if (b.systems) {
                    b.systems.forEach((sys, sIdx) => {
                        buildOvalOrbitLine(bGroup, sys.a, sys.ecc, sys.color);

                        const sysGroup = new THREE.Group();
                        const sAngle = (sIdx * 2.1) + 0.5;
                        const sR = (sys.a * (1 - sys.ecc * sys.ecc)) / (1 + sys.ecc * Math.cos(sAngle));
                        sysGroup.position.set(Math.cos(sAngle) * sR, 0, Math.sin(sAngle) * sR);

                        // Alien Host Star
                        const starGeo = new THREE.SphereGeometry(sys.r, 24, 24);
                        const starMat = new THREE.MeshBasicMaterial({ color: sys.color });
                        const alienStar = new THREE.Mesh(starGeo, starMat);
                        sysGroup.add(alienStar);

                        // Star Halo
                        const haloGeo = new THREE.SphereGeometry(sys.r * 1.5, 20, 20);
                        const haloMat = new THREE.MeshBasicMaterial({ color: sys.color, transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, side: THREE.BackSide });
                        alienStar.add(new THREE.Mesh(haloGeo, haloMat));

                        alienStar.userData = {
                            id: `${b.id}_star_${sIdx}`,
                            name: sys.name,
                            type: "star_system",
                            sector: b.name,
                            frequency: "741 Hz",
                            energy_signature: "Extragalactic Alien Fusion Engine",
                            lore: `An alien star system flourishing inside the ${b.name}, holding living exoplanets in Keplerian harmony.`,
                            color: sys.color,
                            mesh: alienStar,
                            sysGroup: sysGroup,
                            a: sys.a,
                            ecc: sys.ecc,
                            angle: sAngle,
                            baseSpeed: 0.0008,
                            starRadius: sys.r
                        };
                        stellarObjects.push(alienStar);
                        sisterSystemsGroup.push(alienStar);

                        // Orbiting Alien Exoplanets
                        sys.planets.forEach(p => {
                            buildOvalOrbitLine(sysGroup, p.a, p.ecc, p.color);

                            const pGeo = new THREE.SphereGeometry(p.r, 20, 20);
                            const pMat = new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.7 });
                            const alienPlanet = new THREE.Mesh(pGeo, pMat);

                            const pAngle = Math.random() * Math.PI * 2;
                            const pR = (p.a * (1 - p.ecc * p.ecc)) / (1 + p.ecc * Math.cos(pAngle));
                            alienPlanet.position.set(Math.cos(pAngle) * pR, 0, Math.sin(pAngle) * pR);

                            alienPlanet.userData = {
                                id: p.name.toLowerCase().replace(/[^a-z0-9]/g, "_"),
                                name: p.name,
                                type: "exoplanet",
                                sector: sys.name,
                                frequency: "852 Hz",
                                energy_signature: "Extragalactic Alien Biosphere",
                                lore: p.lore,
                                color: p.color,
                                mesh: alienPlanet,
                                a: p.a,
                                ecc: p.ecc,
                                angle: pAngle,
                                speed: 0.015,
                                radius: p.r
                            };
                            sysGroup.add(alienPlanet);
                            planetaryBodies.push(alienPlanet);
                        });

                        bGroup.add(sysGroup);
                    });
                }
            } else {
                // Prime Observable Bubble Universe: Register central reference
                bMesh.userData = {
                    id: b.id,
                    name: b.name,
                    type: "bubble_universe",
                    sector: "Prime Cosmological Framework",
                    frequency: "432 Hz",
                    lore: b.lore,
                    color: "#00f3ff",
                    mesh: bMesh,
                    radius: b.radius
                };
                bubbleUniverses.push(bMesh);
                stellarObjects.push(bMesh);
            }

            bubbleMultiverseGroup.add(bGroup);
        });

        // 4. 12,000 Inflaton Quantum Bubble Seeds in the Infinite Quantum Ocean (1.5M - 3.5M units)
        const qCount = 12000;
        const qPos = new Float32Array(qCount * 3);
        const qColors = new Float32Array(qCount * 3);
        const qPalette = [
            new THREE.Color(0x00f3ff),
            new THREE.Color(0xff007f),
            new THREE.Color(0x9d4edd),
            new THREE.Color(0x38ef7d),
            new THREE.Color(0xffd166),
            new THREE.Color(0x00d4ff)
        ];

        for (let i = 0; i < qCount; i++) {
            const r = 1200000 + Math.pow(Math.random(), 0.5) * 2300000;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(Math.random() * 2 - 1);

            qPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            qPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            qPos[i * 3 + 2] = r * Math.cos(phi);

            const c = qPalette[Math.floor(Math.random() * qPalette.length)];
            qColors[i * 3] = c.r;
            qColors[i * 3 + 1] = c.g;
            qColors[i * 3 + 2] = c.b;
        }

        const qGeo = new THREE.BufferGeometry();
        qGeo.setAttribute("position", new THREE.BufferAttribute(qPos, 3));
        qGeo.setAttribute("color", new THREE.BufferAttribute(qColors, 3));

        const qMat = new THREE.PointsMaterial({
            size: isMobile ? 3.0 : 4.5,
            vertexColors: true,
            map: createGaussianStarTexture(),
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        bubbleMultiverseGroup.add(new THREE.Points(qGeo, qMat));

        universeRoot.add(bubbleMultiverseGroup);
    }

    /* =========================================================================
       SYSTEMS & WORLDS CATALOG POPULATOR (For Modal Sheet & Quick Navigation)
       ========================================================================= */

    function loadSystemCatalog() {
        if (!anomaliesList) return;
        anomaliesList.innerHTML = "";

        const catalog = [];
        stellarObjects.forEach(s => catalog.push(s.userData));
        planetaryBodies.forEach(p => catalog.push(p.userData));

        catalog.forEach(item => {
            const card = document.createElement("div");
            card.className = "anomaly-card";
            card.innerHTML = `
                <div class="anomaly-header">
                    <span class="anomaly-tag" style="background:${item.color || '#00f3ff'}">${(item.type || 'OBJECT').toUpperCase()}</span>
                    <h4>${item.name}</h4>
                </div>
                <div class="anomaly-meta">${item.sector || 'Cosmic System'}</div>
            `;
            card.addEventListener("click", () => {
                const targetObj = planetaryBodies.find(p => p.userData.id === item.id) ||
                                  stellarObjects.find(s => s.userData.id === item.id);
                if (targetObj) selectCelestialTarget(targetObj);
            });
            anomaliesList.appendChild(card);
        });
    }

    /* =========================================================================
       SCALE RIBBON & CONTINUOUS AUTO-DETECTION
       ========================================================================= */

    function setupScaleRibbon() {
        document.querySelectorAll(".scale-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".scale-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                const scaleKey = btn.dataset.scale;
                flyToScale(scaleKey);
            });
        });

        if (closeChronicleBtn) {
            closeChronicleBtn.addEventListener("click", () => {
                scaleChronicleCard.classList.add("collapsed");
            });
        }
    }

    function flyToScale(scaleKey) {
        if (soundEnabled && window.aetheriaAudio) window.aetheriaAudio.playWarpSound();
        scene.updateMatrixWorld(true);

        if (scaleKey === "planetary") {
            const earthPos = new THREE.Vector3();
            if (earthMesh) earthMesh.getWorldPosition(earthPos);
            else if (solSystemGroup) solSystemGroup.getWorldPosition(earthPos);
            targetLookAt = earthPos.clone();
            targetCameraPos = earthPos.clone().add(new THREE.Vector3(0, 2.8, 8.5));
            showToast("Flying To: 🌍 Earth Close-Up");
        } else if (scaleKey === "solar_system") {
            const sunPos = new THREE.Vector3();
            if (solSystemGroup) solSystemGroup.getWorldPosition(sunPos);
            targetLookAt = sunPos.clone();
            targetCameraPos = sunPos.clone().add(new THREE.Vector3(0, 32, 95));
            showToast("Flying To: ☀️ Heliosphere Solar System");
        } else if (scaleKey === "stellar_neighborhood") {
            const hgPos = new THREE.Vector3();
            if (blueHypergiant) blueHypergiant.getWorldPosition(hgPos);
            targetLookAt = hgPos.clone();
            targetCameraPos = hgPos.clone().add(new THREE.Vector3(0, 380, 1050));
            showToast("Flying To: 💎 Cygnus Blue Hypergiant");
        } else if (scaleKey === "milky_way") {
            targetLookAt = new THREE.Vector3(0, 0, 0);
            targetCameraPos = new THREE.Vector3(0, 7500, 13000);
            showToast("Flying To: 🌌 Milky Way Spiral & Sgr A*");
        } else if (scaleKey === "supercluster") {
            targetLookAt = new THREE.Vector3(0, 0, 0);
            targetCameraPos = new THREE.Vector3(0, 28000, 55000);
            showToast("Flying To: 🌀 Laniakea Mega-Cluster");
        } else if (scaleKey === "cosmic_web") {
            targetLookAt = new THREE.Vector3(0, 0, 0);
            targetCameraPos = new THREE.Vector3(0, 75000, 160000);
            showToast("Flying To: 🕸️ Observable Cosmic Web");
        } else if (scaleKey === "multiverse_matrix") {
            targetLookAt = new THREE.Vector3(0, 0, 0);
            targetCameraPos = new THREE.Vector3(0, 180000, 420000);
            showToast("Flying To: 🫧 Bubble Multiverse");
        }
    }

    function updateAutoDetectedScale() {
        if (targetCameraPos) return;
        scene.updateMatrixWorld(true);

        const camPos = camera.position;
        const sunPos = new THREE.Vector3();
        if (solSystemGroup) solSystemGroup.getWorldPosition(sunPos);
        const hgPos = new THREE.Vector3();
        if (blueHypergiant) blueHypergiant.getWorldPosition(hgPos);

        const distToSun = camPos.distanceTo(sunPos);
        const distToHg = camPos.distanceTo(hgPos);
        const distToOrigin = camPos.length();

        let newScaleKey;
        if (distToSun < 38) {
            newScaleKey = "planetary";
        } else if (distToSun < 320) {
            newScaleKey = "solar_system";
        } else if (distToHg < 2400) {
            newScaleKey = "stellar_neighborhood";
        } else if (distToOrigin <= 18000) {
            newScaleKey = "milky_way";
        } else if (distToOrigin <= 85000) {
            newScaleKey = "supercluster";
        } else if (distToOrigin <= 600000) {
            newScaleKey = "cosmic_web";
        } else {
            newScaleKey = "multiverse_matrix";
        }

        if (newScaleKey !== detectedScaleKey) {
            detectedScaleKey = newScaleKey;
            const matchingTier = SCALE_TIERS.find(t => t.key === detectedScaleKey);
            if (matchingTier) {
                document.querySelectorAll(".scale-btn").forEach(btn => {
                    btn.classList.toggle("active", btn.dataset.scale === detectedScaleKey);
                });

                if (microScale) microScale.innerText = "View: " + matchingTier.badge;
                if (scaleBadgeText) scaleBadgeText.innerText = matchingTier.badge;
                if (scaleChronicleText) scaleChronicleText.innerText = `"${matchingTier.chronicle}"`;
            }
        }
    }

    /* =========================================================================
       SELECTION, RAYCASTING & INTERACTION
       ========================================================================= */

    function selectCelestialTarget(target) {
        selectedTarget = target;
        focusedObject = target;
        const data = target.userData;

        closeAllModals();

        if (soundEnabled && window.aetheriaAudio) {
            const freqNum = parseFloat(data.frequency) || 432;
            window.aetheriaAudio.playChime(null, freqNum);
        }

        if (inspectorTitle) {
            inspectorTitle.innerText = data.name;
            inspectorTitle.style.color = data.color || "#00f3ff";
        }
        if (inspectorSector) inspectorSector.innerText = data.sector || "Cosmic Sector";
        if (inspectorFreq) inspectorFreq.innerText = data.frequency || "Harmonic Orbit";
        if (inspectorEnergy) inspectorEnergy.innerText = data.energy_signature || "Stable World";
        if (inspectorLore) {
            inspectorLore.innerText = data.lore;
            inspectorLore.style.borderLeftColor = data.color || "#00f3ff";
        }
        if (oracleOutput) oracleOutput.style.display = "none";
        if (inspector) inspector.classList.remove("collapsed");

        flyToTargetObject(target);
    }

    function flyToTargetObject(target) {
        const worldPos = new THREE.Vector3();
        if (target.getWorldPosition) target.getWorldPosition(worldPos);

        const type = target.userData.type;
        let offsetDist;
        if (type === "planet" || type === "exoplanet") {
            const radius = target.userData.radius || 1.4;
            offsetDist = Math.max(radius * 3.8, 5.0);
        } else if (type === "star_system" || type === "star") {
            const sRadius = target.userData.starRadius || 7.0;
            offsetDist = Math.max(sRadius * 3.4, 28.0);
        } else if (type === "blue_hypergiant") {
            offsetDist = 180.0;
        } else if (type === "galaxy") {
            offsetDist = (target.userData.radius || 1200) * 0.9;
        } else if (type === "bubble_universe") {
            offsetDist = (target.userData.radius || 24000) * 0.42;
        } else {
            offsetDist = 32.0;
        }

        targetCameraPos = worldPos.clone().add(new THREE.Vector3(offsetDist, offsetDist * 0.42, offsetDist));
        targetLookAt = worldPos.clone();
        focusedObject = target;
        prevFocusPos.copy(worldPos);
    }

    function onCanvasClick(event) {
        if (event.target.closest(".dynamic-capsule") || event.target.closest(".bottom-dock") || event.target.closest(".scale-ribbon") || event.target.closest(".slide-modal") || event.target.closest(".intro-hook-chip") || event.target.closest(".zen-exit-floating-btn")) {
            return;
        }

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
            if (e.target.closest(".dynamic-capsule") || event.target.closest(".bottom-dock") || event.target.closest(".scale-ribbon") || event.target.closest(".slide-modal") || event.target.closest(".intro-hook-chip") || event.target.closest(".zen-exit-floating-btn")) {
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

    function setupKeyboardFlightControls() {
        window.addEventListener("keydown", (e) => {
            if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
            activeKeys[e.code] = true;
            if (["KeyW", "KeyS", "KeyA", "KeyD", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space", "KeyC", "KeyR", "KeyF", "KeyQ", "KeyE"].includes(e.code)) {
                e.preventDefault();
            }
        });
        window.addEventListener("keyup", (e) => {
            activeKeys[e.code] = false;
        });
    }

    function handleKeyboardFlight(delta) {
        if (!controls || !camera) return;

        const forward = new THREE.Vector3();
        camera.getWorldDirection(forward);
        const up = camera.up.clone().normalize();
        const right = new THREE.Vector3().crossVectors(forward, up).normalize();

        const camDist = camera.position.length();
        const isBoost = activeKeys["ShiftLeft"] || activeKeys["ShiftRight"];
        const boostMult = isBoost ? 5.0 : 1.0;
        const flightSpeed = Math.max(14.0, camDist * 0.12) * boostMult * delta;

        const moveVec = new THREE.Vector3();
        if (activeKeys["KeyW"] || activeKeys["ArrowUp"]) moveVec.addScaledVector(forward, flightSpeed);
        if (activeKeys["KeyS"] || activeKeys["ArrowDown"]) moveVec.addScaledVector(forward, -flightSpeed);
        if (activeKeys["KeyA"] || activeKeys["ArrowLeft"]) moveVec.addScaledVector(right, -flightSpeed);
        if (activeKeys["KeyD"] || activeKeys["ArrowRight"]) moveVec.addScaledVector(right, flightSpeed);
        if (activeKeys["KeyR"] || activeKeys["Space"]) moveVec.addScaledVector(up, flightSpeed);
        if (activeKeys["KeyF"] || activeKeys["KeyC"]) moveVec.addScaledVector(up, -flightSpeed);

        if (moveVec.lengthSq() > 0.0001) {
            camera.position.add(moveVec);
            controls.target.add(moveVec);
            targetCameraPos = null;
            focusedObject = null; // Free starship flight disengages orbital lock
        }
    }

    function setupHoverReticle() {
        hoverReticle = document.getElementById("cosmic-hover-reticle");
        window.addEventListener("mousemove", (e) => {
            if (!hoverReticle) return;
            if (isZenMode) {
                hoverReticle.classList.remove("active");
                return;
            }
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            const hitTargets = [];
            planetaryBodies.forEach(p => hitTargets.push(p.userData.mesh || p));
            stellarObjects.forEach(s => hitTargets.push(s.userData.mesh || s));

            const intersects = raycaster.intersectObjects(hitTargets, false);
            if (intersects.length > 0) {
                let hit = intersects[0].object;
                if (hit.parent && hit.parent.userData.name) hit = hit.parent;
                const d = hit.userData;
                if (d && d.name) {
                    hoverReticle.style.left = `${e.clientX}px`;
                    hoverReticle.style.top = `${e.clientY}px`;
                    hoverReticle.innerHTML = `<span style="color:${d.color || '#00f3ff'}">✦ ${d.name}</span> <span style="opacity:0.7">• Click to Enter</span>`;
                    hoverReticle.classList.add("active");
                    document.body.style.cursor = "pointer";
                    return;
                }
            }
            hoverReticle.classList.remove("active");
            document.body.style.cursor = "default";
        });
    }

    function checkRaycastHit() {
        const hitTargets = [];
        planetaryBodies.forEach(p => hitTargets.push(p.userData.mesh || p));
        stellarObjects.forEach(s => hitTargets.push(s.userData.mesh || s));

        const intersects = raycaster.intersectObjects(hitTargets, false);
        if (intersects.length > 0) {
            let hit = intersects[0].object;
            if (hit.parent && hit.parent.userData.name) hit = hit.parent;
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
        }, 45000);
    }

    function exitZenMode() {
        isZenMode = false;
        document.body.classList.remove("zen-mode");
        const capsuleZenBtn = document.getElementById("capsule-zen-btn");
        if (capsuleZenBtn) capsuleZenBtn.classList.remove("active");
        showToast("Interface Restored");
    }

    /* =========================================================================
       ERGONOMIC CONTROLS, TUNING DECK & AUDIO
       ========================================================================= */

    function setupErgonomicControls() {
        if (dismissHookBtn) {
            dismissHookBtn.addEventListener("click", () => {
                introHookChip.classList.add("dismissed");
                if (window.aetheriaAudio && !window.aetheriaAudio.isPlaying) toggleAudio();
            });
        }

        if (zenExitBtn) {
            zenExitBtn.addEventListener("click", exitZenMode);
        }

        const capsuleAudioBtn = document.getElementById("capsule-audio-btn");
        const dockAudioBtn = document.getElementById("dock-audio-btn");
        const tuningAudioBtn = document.getElementById("tuning-audio-toggle-btn");
        const audioIconSpan = document.getElementById("audio-icon-span");
        const dockAudioIcon = document.getElementById("dock-audio-icon");
        const audioStatusLabel = document.getElementById("audio-status-label");

        function toggleAudio() {
            soundEnabled = !soundEnabled;
            let active = false;
            if (window.aetheriaAudio) {
                active = window.aetheriaAudio.toggle();
            }
            const icon = active ? "🔊" : "🔇";
            if (audioIconSpan) audioIconSpan.innerText = icon;
            if (dockAudioIcon) dockAudioIcon.innerText = icon;
            if (audioStatusLabel) audioStatusLabel.innerText = active ? "Active" : "Muted";
            if (capsuleAudioBtn) capsuleAudioBtn.classList.toggle("active", active);
            if (dockAudioBtn) dockAudioBtn.classList.toggle("active", active);
            showToast(active ? "Cosmic Soundscape Engaged" : "Audio Muted");
        }

        if (capsuleAudioBtn) capsuleAudioBtn.addEventListener("click", toggleAudio);
        if (dockAudioBtn) dockAudioBtn.addEventListener("click", toggleAudio);
        if (tuningAudioBtn) tuningAudioBtn.addEventListener("click", toggleAudio);

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
                showToast(isZenMode ? "Pure Zen View • Tap Eye to Restore" : "Interface Restored");
            });
        }

        const dockExploreBtn = document.getElementById("dock-explore-btn");
        if (dockExploreBtn) {
            dockExploreBtn.addEventListener("click", () => {
                closeAllModals();
                targetCameraPos = new THREE.Vector3(0, 35, 120);
                targetLookAt = new THREE.Vector3(0, 0, 0);
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

        const flyToTargetBtn = document.getElementById("fly-to-target-btn");
        if (flyToTargetBtn) {
            flyToTargetBtn.addEventListener("click", () => {
                if (selectedTarget) flyToTargetObject(selectedTarget);
            });
        }

        const playTargetSoundBtn = document.getElementById("play-target-sound-btn");
        if (playTargetSoundBtn) {
            playTargetSoundBtn.addEventListener("click", () => {
                if (selectedTarget && window.aetheriaAudio) {
                    const freqNum = parseFloat(selectedTarget.userData.frequency) || 432;
                    window.aetheriaAudio.playChime(null, freqNum);
                    showToast(`Harmonic: ${freqNum.toFixed(1)} Hz`);
                }
            });
        }

        // FPS Selector Pills
        document.querySelectorAll(".fps-pill").forEach(pill => {
            pill.addEventListener("click", () => {
                document.querySelectorAll(".fps-pill").forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                const fps = parseInt(pill.dataset.fps);
                targetFpsSetting = fps;
                fixedPhysicsDt = 1.0 / fps;
                const engineFpsBadge = document.getElementById("engine-fps-badge");
                if (engineFpsBadge) engineFpsBadge.innerText = `${fps} Hz ${fps === 240 ? "Max" : "Engine"}`;
                showToast(`Simulation Tuned: ${fps} FPS Target`);
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

        const galaxySpeedSlider = document.getElementById("galaxy-speed-slider");
        const galaxySpeedVal = document.getElementById("galaxy-speed-val");
        if (galaxySpeedSlider) {
            galaxySpeedSlider.addEventListener("input", (e) => {
                galaxySpeedMult = parseFloat(e.target.value);
                if (galaxySpeedVal) galaxySpeedVal.innerText = galaxySpeedMult.toFixed(1) + "x";
            });
        }

        const starSizeSlider = document.getElementById("star-size-slider");
        const starSizeVal = document.getElementById("star-size-val");
        if (starSizeSlider) {
            starSizeSlider.addEventListener("input", (e) => {
                starSize = parseFloat(e.target.value);
                if (particleSystem) particleSystem.material.size = isMobile ? starSize * 1.3 : starSize;
                if (starSizeVal) starSizeVal.innerText = starSize.toFixed(1) + " px";
            });
        }

        const resetCamBtn = document.getElementById("reset-cam-btn");
        if (resetCamBtn) {
            resetCamBtn.addEventListener("click", () => {
                targetCameraPos = new THREE.Vector3(0, 35, 120);
                targetLookAt = new THREE.Vector3(0, 0, 0);
                closeAllModals();
            });
        }

        const snapshotBtn = document.getElementById("snapshot-btn");
        if (snapshotBtn) snapshotBtn.addEventListener("click", captureScreenshot);

        // NVIDIA Nemotron Cosmic Oracle Transmission
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
                    body: JSON.stringify({ prompt: text, anomaly: name })
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

    let warpVoyageIndex = 0;
    function triggerWarpJump() {
        if (isWarping) return;
        isWarping = true;
        closeAllModals();

        if (soundEnabled && window.aetheriaAudio) window.aetheriaAudio.playWarpSound();

        const ninesStages = [
            { speed: "0.99c", gamma: "7.09", earthTime: "1 Flight Day = 1 Week on Earth" },
            { speed: "0.9999c", gamma: "70.7", earthTime: "1 Flight Day = 2.3 Months on Earth" },
            { speed: "0.999999c", gamma: "707.1", earthTime: "1 Flight Day = 1.94 Years on Earth" },
            { speed: "0.99999999c", gamma: "7,071", earthTime: "1 Flight Day = 19.4 Years on Earth" },
            { speed: "0.9999999999c", gamma: "70,710", earthTime: "1 Flight Day = 193.7 Years on Earth" }
        ];

        let stageIdx = 0;
        const stageInterval = setInterval(() => {
            if (!isWarping || stageIdx >= ninesStages.length) {
                clearInterval(stageInterval);
                return;
            }
            const s = ninesStages[stageIdx];
            if (microFps) microFps.innerText = `🚀 ${s.speed} • Lorentz γ: ${s.gamma} • ${s.earthTime}`;
            stageIdx++;
        }, 340);

        showToast("⚡ ACCELERATING THROUGH THE NINES • LORENTZ CONTRACTION ACTIVE");

        let start = performance.now();
        let duration = 2400;

        function warpStep(now) {
            let elapsed = now - start;
            let progress = elapsed / duration;

            if (progress < 0.5) {
                warpFactor = 1.0 + (progress * 2) * 16.0;
            } else if (progress < 1.0) {
                warpFactor = 17.0 - ((progress - 0.5) * 2) * 16.0;
            } else {
                warpFactor = 1.0;
                isWarping = false;
                clearInterval(stageInterval);

                warpVoyageIndex = (warpVoyageIndex + 1) % 4;
                if (warpVoyageIndex === 1) {
                    // Voyage 1: The Polar View No Human Has Ever Seen
                    targetCameraPos = new THREE.Vector3(0, 16000, 600);
                    targetLookAt = new THREE.Vector3(0, 0, 0);
                    showToast("🌌 TRIP 1: THE UNSEEN VIEW • 16,000 LY Above Galactic Pole Looking Down");
                } else if (warpVoyageIndex === 2) {
                    // Voyage 2: Sagittarius A* Relativistic Event Horizon
                    targetCameraPos = new THREE.Vector3(0, 140, 360);
                    targetLookAt = new THREE.Vector3(0, 0, 0);
                    showToast("🕳️ TRIP 2: SAGITTARIUS A* • 26,000 LY in a Weekend (52,000 Earth Years Passed)");
                } else if (warpVoyageIndex === 3) {
                    // Voyage 3: Hubble Expansion Edge & Multiverse
                    targetCameraPos = new THREE.Vector3(0, 220000, 520000);
                    targetLookAt = new THREE.Vector3(0, 0, 0);
                    showToast("🫧 TRIP 3: HUBBLE EXPANSION HORIZON • Where Space Outruns Light");
                } else {
                    // Voyage 4: Return to Earth (Leading the target across 40 LY)
                    const sunPos = new THREE.Vector3();
                    if (solSystemGroup) solSystemGroup.getWorldPosition(sunPos);
                    targetCameraPos = sunPos.clone().add(new THREE.Vector3(0, 32, 95));
                    targetLookAt = sunPos.clone();
                    showToast("☀️ HOMECOMING: Intercepting Solar System (Earth Moved 40 LY Along Orbit!)");
                }
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

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    /* =========================================================================
       ULTRA-SMOOTH MAIN ANIMATION LOOP (Real Keplerian Mechanics & Oval Orbits)
       ========================================================================= */

    function animate(time) {
        requestAnimationFrame(animate);

        const delta = Math.min(clock.getDelta(), 0.05);
        frameCount++;
        if (time - lastFpsTime >= 1000) {
            currentFps = Math.round((frameCount * 1000) / (time - lastFpsTime));
            if (capsuleFps) capsuleFps.innerText = currentFps + " FPS";
            if (microFps) microFps.innerText = `${currentFps} FPS • ${targetFpsSetting} Hz Engine`;
            frameCount = 0;
            lastFpsTime = time;
        }

        // Sub-stepping physics accumulator for ultra-smooth 240 Hz numerical fidelity
        physicsAccumulator += delta;
        const maxSubSteps = 4;
        let steps = 0;

        while (physicsAccumulator >= fixedPhysicsDt && steps < maxSubSteps) {
            updatePhysics(fixedPhysicsDt, time);
            physicsAccumulator -= fixedPhysicsDt;
            steps++;
        }

        // Update world matrices after physics simulation
        scene.updateMatrixWorld(true);

        // 1. Starship Manual Flight (WASD / Arrows / Shift)
        handleKeyboardFlight(delta);

        // 2. Dynamic Hierarchical Focal Centering & Relative Orbit Tracking
        const camPos = camera.position;
        const sunPos = new THREE.Vector3();
        if (solSystemGroup) solSystemGroup.getWorldPosition(sunPos);
        const hgPos = new THREE.Vector3();
        if (blueHypergiant) blueHypergiant.getWorldPosition(hgPos);
        const sgrPos = new THREE.Vector3(0, 0, 0);
        const gaPos = new THREE.Vector3(52000, 11000, -42000);

        if (!focusedObject && !targetCameraPos && !isIngress) {
            const distToSun = camPos.distanceTo(sunPos);
            const distToHg = camPos.distanceTo(hgPos);
            const camOriginDist = camPos.length();

            if (distToSun < 380) {
                // Tier 1: Solar System View (Close-up) - Sun is stationary in dead center!
                controls.target.copy(sunPos);
                if (prevSunPos.lengthSq() > 0.001) {
                    const sunDelta = sunPos.clone().sub(prevSunPos);
                    camera.position.add(sunDelta);
                }
            } else if (distToSun < 2800) {
                // Tier 2: Stellar Neighborhood - smoothly blend target from Sun to Blue Hypergiant
                const w = Math.max(0, Math.min(1, (distToSun - 380) / 1000));
                const smoothW = w * w * (3 - 2 * w);
                const blendedTarget = new THREE.Vector3().lerpVectors(sunPos, hgPos, smoothW);
                controls.target.lerp(blendedTarget, 0.12);
            } else if (distToHg < 18000) {
                // Tier 3: Milky Way Galactic Scale - smoothly blend from Blue Hypergiant to Sagittarius A*
                const w = Math.max(0, Math.min(1, (distToHg - 2800) / 7500));
                const smoothW = w * w * (3 - 2 * w);
                const blendedTarget = new THREE.Vector3().lerpVectors(hgPos, sgrPos, smoothW);
                controls.target.lerp(blendedTarget, 0.08);
            } else if (camOriginDist < 85000) {
                // Tier 4: Supercluster Scale - blend from Milky Way to Great Attractor
                const w = Math.max(0, Math.min(1, (camOriginDist - 18000) / 45000));
                const smoothW = w * w * (3 - 2 * w);
                const blendedTarget = new THREE.Vector3().lerpVectors(sgrPos, gaPos, smoothW * 0.7);
                controls.target.lerp(blendedTarget, 0.06);
            } else {
                // Tier 5: Cosmic Web & Multiverse - macro center
                controls.target.lerp(sgrPos, 0.04);
            }
        } else if (focusedObject && focusedObject.getWorldPosition) {
            const currentFocusPos = new THREE.Vector3();
            focusedObject.getWorldPosition(currentFocusPos);
            controls.target.copy(currentFocusPos);
            if (prevFocusPos.lengthSq() > 0.001 && !targetCameraPos && !isIngress) {
                const focusDelta = currentFocusPos.clone().sub(prevFocusPos);
                camera.position.add(focusDelta);
            }
            prevFocusPos.copy(currentFocusPos);
        }
        prevSunPos.copy(sunPos);

        // Ingress Animation
        if (isIngress) {
            const elapsed = time - ingressStart;
            const progress = Math.min(1.0, elapsed / ingressDuration);
            const ease = 1 - Math.pow(1 - progress, 3);
            camera.position.lerpVectors(startPos, targetOrbitPos, ease);
            controls.target.copy(sunPos);
            if (progress >= 1.0) isIngress = false;
        }

        // Camera Smooth Flying (Lerp)
        if (targetCameraPos && !isIngress) {
            const lerpFactor = 1.0 - Math.exp(-6.0 * delta);
            camera.position.lerp(targetCameraPos, lerpFactor);
            controls.target.lerp(targetLookAt, lerpFactor);
            currentLookAt.copy(controls.target);
            if (camera.position.distanceTo(targetCameraPos) < 0.25) {
                targetCameraPos = null;
            }
        }

        // Distance-adaptive visibility of macro cosmological structures
        const camDistToOrigin = camera.position.length();
        if (superclusterGroup) superclusterGroup.visible = true;
        if (cosmicWebGroup) cosmicWebGroup.visible = true;
        if (bubbleMultiverseGroup) bubbleMultiverseGroup.visible = true;

        // Automatically determine cosmological scale based on camera distance
        updateAutoDetectedScale();

        controls.update();
        renderer.render(scene, camera);
    }

    function updatePhysics(dt, time) {
        const effSpeed = speedMult * warpFactor * dt * 60.0;

        // 1. Blue Hypergiant Axial Rotation & Galactic Orbit around Sagittarius A*
        if (blueHypergiant) {
            blueHypergiant.rotation.y += 0.008 * effSpeed; // Spins on its 14° tilted axis
        }
        if (blueHypergiantGroup) {
            hgGalacticAngle += 0.00012 * effSpeed * galaxySpeedMult;
            blueHypergiantGroup.position.x = Math.cos(hgGalacticAngle) * hgGalacticRadius;
            blueHypergiantGroup.position.z = Math.sin(hgGalacticAngle) * hgGalacticRadius;
        }

        // 2. Our Sun: Revolves along its Oval Orbit around Blue Hypergiant
        const solData = stellarObjects.find(s => s.userData.id === "sol");
        if (solData && solSystemGroup) {
            const d = solData.userData;
            // Kepler's Second Law: faster at perihelion, slower at aphelion
            const curR = (d.semiA * (1 - d.ecc * d.ecc)) / (1 + d.ecc * Math.cos(d.angle));
            const speedFactor = Math.pow(d.semiA / curR, 1.6);
            d.angle += d.baseSpeed * speedFactor * effSpeed;

            solSystemGroup.position.x = Math.cos(d.angle) * curR;
            solSystemGroup.position.z = Math.sin(d.angle) * curR;
            d.mesh.rotation.y += 0.015 * effSpeed; // Sun rotates on its own axis
        }

        // 3. Sister Systems Revolve along their Oval Orbits around Blue Hypergiant
        sisterSystemsGroup.forEach(star => {
            const d = star.userData;
            const curR = (d.a * (1 - d.ecc * d.ecc)) / (1 + d.ecc * Math.cos(d.angle));
            const speedFactor = Math.pow(d.a / curR, 1.5);
            d.angle += (d.baseSpeed || 0.001) * speedFactor * effSpeed;

            d.sysGroup.position.x = Math.cos(d.angle) * curR;
            d.sysGroup.position.z = Math.sin(d.angle) * curR;
            star.rotation.y += 0.012 * effSpeed; // Star spins on its axis
        });

        // 4. Planets: Real Oval Orbits + Axial Rotation (Obliquity)
        planetaryBodies.forEach(pObj => {
            const d = pObj.userData;
            if (d.a && d.ecc !== undefined) {
                // Kepler's Second Law: Variable velocity
                const curR = (d.a * (1 - d.ecc * d.ecc)) / (1 + d.ecc * Math.cos(d.angle));
                const speedFactor = Math.pow(d.a / curR, 1.7);
                d.angle += d.speed * speedFactor * effSpeed;

                if (d.tiltGroup) {
                    d.tiltGroup.position.x = Math.cos(d.angle) * curR;
                    d.tiltGroup.position.z = Math.sin(d.angle) * curR;
                } else {
                    pObj.position.x = Math.cos(d.angle) * curR;
                    pObj.position.z = Math.sin(d.angle) * curR;
                }

                // Planet rotates continuously around its own tilted axis
                if (d.mesh) {
                    d.mesh.rotation.y += 0.022 * effSpeed;
                }
            }
        });

        // Earth Atmospheric Cloud Parallax
        if (earthClouds) {
            earthClouds.rotation.y += 0.026 * effSpeed;
        }

        // Moon Orbit around Earth
        if (moonMesh) {
            const moonAngle = time * 0.003 * effSpeed;
            moonMesh.position.x = Math.cos(moonAngle) * 3.4;
            moonMesh.position.z = Math.sin(moonAngle) * 3.4;
            moonMesh.rotation.y += 0.012 * effSpeed;
        }

        // 5. Sagittarius A* Relativistic Accretion Furnace Swirl
        if (sgrAccretionDisk) {
            sgrAccretionDisk.rotation.z += 0.045 * effSpeed; // Spinning at relativistic velocity
        }
        if (sgrJetNorth && sgrJetSouth) {
            sgrJetNorth.rotation.y += 0.02 * effSpeed;
            sgrJetSouth.rotation.y += 0.02 * effSpeed;
        }

        // 6. Milky Way 65,000 Stars: PURE ANALYTICAL ROTATION (Zero Shaking!)
        if (particleGeometry && particlePositions && particlePhases) {
            const pos = particlePositions;
            const phases = particlePhases;
            const radii = particleRadii;
            const speeds = particleSpeeds;
            const count = particlesCount;
            const gSpeed = effSpeed * galaxySpeedMult;

            for (let i = 0; i < count; i++) {
                phases[i] += speeds[i] * 0.015 * gSpeed;
                const theta = phases[i];
                const r = radii[i];
                const i3 = i * 3;

                pos[i3] = Math.cos(theta) * r;
                pos[i3 + 2] = Math.sin(theta) * r;
            }
            particleGeometry.attributes.position.needsUpdate = true;
        }

        // 7. Extragalactic Swirl & Bubble Multiverse Inflaton Drift
        if (superclusterGroup) superclusterGroup.rotation.y += 0.00018 * effSpeed;
        if (cosmicWebGroup) cosmicWebGroup.rotation.y += 0.00009 * effSpeed;
        if (bubbleMultiverseGroup) bubbleMultiverseGroup.rotation.y += 0.00005 * effSpeed;
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

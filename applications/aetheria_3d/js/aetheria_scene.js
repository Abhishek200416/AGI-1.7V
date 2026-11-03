/**
 * AETHERIA 3D • Interactive WebGL 3D Cosmos Engine (Desktop & Mobile Optimized)
 * =============================================================================
 * Real-time procedural universe built with Three.js.
 * Dynamic particle physics, orbital mechanics, interactive raycasting,
 * mobile touch tap detection, and audio-reactive flare rendering.
 * =============================================================================
 */

(function () {
    let scene, camera, renderer, controls;
    let coreGroup, particleSystem, anomalyGroup;
    let particlesCount = 25000;
    let particlePositions, particleVelocities, particleColors, particleGeometry;
    let raycaster, mouse;
    let anomalies = [];
    let selectedAnomaly = null;

    // Device detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;

    // Simulation tuning
    let speedMult = 1.0;
    let gravityMult = 1.0;
    let isWarping = false;
    let warpFactor = 1.0;
    let activeTheme = "violet";

    // Camera target for smooth tweening
    let targetCameraPos = null;
    let targetLookAt = new THREE.Vector3(0, 0, 0);
    let currentLookAt = new THREE.Vector3(0, 0, 0);

    // Performance telemetry
    let lastTime = performance.now();
    let frameCount = 0;
    let fps = 60;

    const container = document.getElementById("canvas-container");
    const fpsVal = document.getElementById("fps-val");
    const particleCountVal = document.getElementById("particle-count-val");
    const leftControls = document.getElementById("left-controls");
    const inspector = document.getElementById("right-inspector");
    const inspectorTitle = document.getElementById("inspector-title");
    const inspectorSector = document.getElementById("inspector-sector");
    const inspectorFreq = document.getElementById("inspector-freq");
    const inspectorLore = document.getElementById("inspector-lore");
    const inspectorEnergy = document.getElementById("inspector-energy");
    const oracleOutput = document.getElementById("oracle-output");

    // Color Theme Palettes
    const PALETTES = {
        violet: {
            core: 0x9d4edd,
            ring: 0x00f3ff,
            dust1: new THREE.Color(0x9d4edd),
            dust2: new THREE.Color(0x00f3ff),
            dust3: new THREE.Color(0xff007f),
            fog: 0x05060b
        },
        aurora: {
            core: 0x38ef7d,
            ring: 0x00f3ff,
            dust1: new THREE.Color(0x38ef7d),
            dust2: new THREE.Color(0x11998e),
            dust3: new THREE.Color(0x00f3ff),
            fog: 0x040a08
        },
        solar: {
            core: 0xffa200,
            ring: 0xff3838,
            dust1: new THREE.Color(0xffd166),
            dust2: new THREE.Color(0xff5e36),
            dust3: new THREE.Color(0xffffff),
            fog: 0x0c0602
        },
        void: {
            core: 0x718096,
            ring: 0x4a5568,
            dust1: new THREE.Color(0xa0aec0),
            dust2: new THREE.Color(0x4a5568),
            dust3: new THREE.Color(0x2d3748),
            fog: 0x030305
        }
    };

    function init() {
        // Adjust particle count for mobile performance
        if (isMobile) {
            particlesCount = 14000;
        }

        // 1. Scene & Atmosphere
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(PALETTES.violet.fog, 0.0065);

        // 2. Camera (Slightly further on mobile for broader perspective)
        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
        camera.position.set(0, isMobile ? 36 : 30, isMobile ? 96 : 85);

        // 3. Renderer with ACES Filmic Tone Mapping (capped pixel ratio on mobile)
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.25;
        container.appendChild(renderer.domElement);

        // 4. Orbit Controls (Configured for smooth touch gestures)
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxDistance = 350;
        controls.minDistance = 12;
        controls.touches = {
            ONE: THREE.TOUCH.ROTATE,
            TWO: THREE.TOUCH.DOLLY_PAN
        };

        // 5. Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x00f3ff, 3, 150);
        pointLight1.position.set(0, 0, 0);
        scene.add(pointLight1);

        // 6. Raycasting & Mouse / Touch Coordinates
        raycaster = new THREE.Raycaster();
        raycaster.params.Points.threshold = 1.0;
        mouse = new THREE.Vector2(-999, -999);

        // 7. Build Scene Components
        createCentralCore();
        createParticleUniverse(particlesCount);
        createCelestialAnomalies();

        // 8. Event Listeners (Desktop & Mobile)
        window.addEventListener("resize", onWindowResize);
        window.addEventListener("mousemove", onMouseMove);
        window.addEventListener("click", onCanvasClick);

        // Mobile touch tap detection
        setupTouchInteraction();

        setupUIControls();

        // Start render loop
        animate(performance.now());
    }

    /**
     * Central Pulsating Core / Lumina Star with multi-tier coronal rings.
     */
    function createCentralCore() {
        coreGroup = new THREE.Group();

        // Inner glowing core
        const coreGeo = new THREE.IcosahedronGeometry(6.5, 3);
        const coreMat = new THREE.MeshBasicMaterial({
            color: PALETTES[activeTheme].core,
            wireframe: true,
            transparent: true,
            opacity: 0.85
        });
        const coreMesh = new THREE.Mesh(coreGeo, coreMat);
        coreGroup.add(coreMesh);

        // Second inverted wireframe shell
        const shellGeo = new THREE.IcosahedronGeometry(7.5, 2);
        const shellMat = new THREE.MeshBasicMaterial({
            color: PALETTES[activeTheme].ring,
            wireframe: true,
            transparent: true,
            opacity: 0.35
        });
        const shellMesh = new THREE.Mesh(shellGeo, shellMat);
        coreGroup.add(shellMesh);

        // Coronal Ring 1
        const ringGeo1 = new THREE.RingGeometry(11, 12.5, 64);
        const ringMat1 = new THREE.MeshBasicMaterial({
            color: PALETTES[activeTheme].ring,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.5
        });
        const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
        ring1.rotation.x = Math.PI / 2.3;
        coreGroup.add(ring1);

        // Coronal Ring 2 (Perpendicular)
        const ringGeo2 = new THREE.RingGeometry(15, 16, 64);
        const ring2 = new THREE.Mesh(ringGeo2, ringMat1.clone());
        ring2.rotation.x = -Math.PI / 3;
        ring2.rotation.y = Math.PI / 6;
        coreGroup.add(ring2);

        scene.add(coreGroup);
    }

    /**
     * Dynamic GPU Particle Universe with Keplerian orbital drift.
     */
    function createParticleUniverse(count) {
        if (particleSystem) scene.remove(particleSystem);

        particlesCount = count;
        particlePositions = new Float32Array(count * 3);
        particleVelocities = new Float32Array(count * 3);
        particleColors = new Float32Array(count * 3);

        const palette = PALETTES[activeTheme];

        for (let i = 0; i < count; i++) {
            // Spiral galaxy disk distribution
            const r = Math.pow(Math.random(), 0.6) * 140 + 10;
            const theta = Math.random() * Math.PI * 2 + (r * 0.05); // Spiral arms
            const y = (Math.random() - 0.5) * (18 * Math.exp(-r / 100)); // Thicker at core

            const x = Math.cos(theta) * r;
            const z = Math.sin(theta) * r;

            particlePositions[i * 3] = x;
            particlePositions[i * 3 + 1] = y;
            particlePositions[i * 3 + 2] = z;

            // Keplerian orbital velocity perpendicular to radius
            const speed = Math.sqrt(120 / r) * 0.12;
            particleVelocities[i * 3] = -Math.sin(theta) * speed;
            particleVelocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
            particleVelocities[i * 3 + 2] = Math.cos(theta) * speed;

            // Chromatic color gradient based on radius
            const colorRatio = r / 150;
            const chosenColor = colorRatio < 0.35 ? palette.dust1 : (colorRatio < 0.7 ? palette.dust2 : palette.dust3);
            particleColors[i * 3] = chosenColor.r;
            particleColors[i * 3 + 1] = chosenColor.g;
            particleColors[i * 3 + 2] = chosenColor.b;
        }

        particleGeometry = new THREE.BufferGeometry();
        particleGeometry.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
        particleGeometry.setAttribute("color", new THREE.BufferAttribute(particleColors, 3));

        // Custom canvas circle texture
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

        if (particleCountVal) {
            particleCountVal.innerText = count.toLocaleString();
        }
    }

    /**
     * Interactive Clickable/Tappable Celestial Beacons across the cosmos.
     */
    function createCelestialAnomalies() {
        anomalyGroup = new THREE.Group();
        anomalies = [];

        // Fetch lore from server API
        fetch("/api/lore", { headers: { "ngrok-skip-browser-warning": "true" } })
            .then(res => res.json())
            .then(data => {
                if (data.status === "OK") {
                    setupAnomalyMeshes(data.anomalies);
                }
            })
            .catch(() => {
                // Fallback default anomalies
                setupAnomalyMeshes({
                    chrono_weave: { title: "The Chronos Weave", coordinates: [28.5, 12.0, -15.4], color: "#9d4edd", frequency: "432 Hz", sector: "Sector 01-A", lore: "Temporal convergence vortex." },
                    lumina_axon: { title: "The Lumina Axon", coordinates: [-25.2, -8.4, 22.1], color: "#00f3ff", frequency: "528 Hz", sector: "Sector 04-E", lore: "Superluminal neural conduit." },
                    void_singularity: { title: "The Void Singularity", coordinates: [0.0, -22.0, -28.0], color: "#ff007f", frequency: "108 Hz", sector: "Sector 09-X", lore: "Zero-point dissolution." },
                    quantum_nebula: { title: "The Quantum Nebula", coordinates: [-30.0, 18.0, -10.5], color: "#38ef7d", frequency: "639 Hz", sector: "Sector 12-F", lore: "Superposition cloud." },
                    harmonic_beacon: { title: "The Harmonic Beacon", coordinates: [18.2, 24.0, 20.0], color: "#ffd166", frequency: "741 Hz", sector: "Sector 07-Omega", lore: "Resonant crystalline array." }
                });
            });

        scene.add(anomalyGroup);
    }

    function setupAnomalyMeshes(anomalyData) {
        Object.keys(anomalyData).forEach((key, index) => {
            const info = anomalyData[key];
            const coords = info.coordinates || [0, 0, 0];
            const colorHex = parseInt(info.color.replace("#", "0x"), 16);

            const beaconMeshGroup = new THREE.Group();
            beaconMeshGroup.position.set(coords[0], coords[1], coords[2]);

            // Unique geometry per anomaly
            let geo;
            if (index % 3 === 0) geo = new THREE.OctahedronGeometry(2.5, 1);
            else if (index % 3 === 1) geo = new THREE.DodecahedronGeometry(2.2, 0);
            else geo = new THREE.TorusKnotGeometry(1.6, 0.45, 64, 8);

            const mat = new THREE.MeshBasicMaterial({
                color: colorHex,
                wireframe: true,
                transparent: true,
                opacity: 0.95
            });
            const mesh = new THREE.Mesh(geo, mat);
            beaconMeshGroup.add(mesh);

            // Glowing aura shell (larger hit area on mobile)
            const haloGeo = new THREE.SphereGeometry(isMobile ? 4.5 : 3.6, 16, 16);
            const haloMat = new THREE.MeshBasicMaterial({
                color: colorHex,
                wireframe: true,
                transparent: true,
                opacity: 0.25
            });
            const halo = new THREE.Mesh(haloGeo, haloMat);
            beaconMeshGroup.add(halo);

            // Metadata for raycast inspection
            beaconMeshGroup.userData = {
                id: key,
                title: info.title,
                sector: info.sector || "Cosmic Sector",
                frequency: info.frequency || "432 Hz",
                energy_signature: info.energy_signature || "Stable",
                lore: info.lore || "Cosmic anomaly in deep synchronous orbit.",
                color: info.color,
                mesh: mesh,
                halo: halo,
                basePos: new THREE.Vector3(coords[0], coords[1], coords[2]),
                orbitSpeed: 0.003 + (index * 0.001)
            };

            anomalyGroup.add(beaconMeshGroup);
            anomalies.push(beaconMeshGroup);
        });
    }

    function onMouseMove(event) {
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    function onCanvasClick(event) {
        // Ignore clicks on HUD panels
        if (event.target.closest(".hud-header") || event.target.closest(".left-controls") || event.target.closest(".right-inspector") || event.target.closest(".bottom-bar")) {
            return;
        }

        raycaster.setFromCamera(mouse, camera);
        checkRaycastHit();
    }

    /**
     * Mobile Touch Tap Detection
     */
    function setupTouchInteraction() {
        let touchStartX = 0;
        let touchStartY = 0;
        let touchStartTime = 0;

        window.addEventListener("touchstart", (e) => {
            if (e.touches.length === 1) {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                touchStartTime = performance.now();
            }
        }, { passive: true });

        window.addEventListener("touchend", (e) => {
            // Ignore if tapped on UI panels
            if (e.target.closest(".hud-header") || e.target.closest(".left-controls") || e.target.closest(".right-inspector") || e.target.closest(".bottom-bar")) {
                return;
            }

            if (e.changedTouches.length === 1) {
                const touch = e.changedTouches[0];
                const dx = touch.clientX - touchStartX;
                const dy = touch.clientY - touchStartY;
                const duration = performance.now() - touchStartTime;

                // Tap detection: minimal movement (< 15px) & short duration (< 350ms)
                if (Math.hypot(dx, dy) < 15 && duration < 350) {
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
        anomalies.forEach(grp => {
            hitTargets.push(grp.userData.mesh);
            hitTargets.push(grp.userData.halo);
        });

        const intersects = raycaster.intersectObjects(hitTargets, false);
        if (intersects.length > 0) {
            const hitGroup = intersects[0].object.parent;
            selectAnomaly(hitGroup);
        }
    }

    function selectAnomaly(group) {
        selectedAnomaly = group;
        const data = group.userData;

        // Close left controls on mobile to avoid screen clutter
        if (leftControls) {
            leftControls.classList.add("collapsed");
            const controlsToggleBtn = document.getElementById("controls-toggle-btn");
            if (controlsToggleBtn) controlsToggleBtn.classList.remove("active");
        }

        // Play harmonic chime
        if (window.aetheriaAudio) {
            const freqNum = parseFloat(data.frequency) || 432;
            window.aetheriaAudio.playChime(null, freqNum);
        }

        // Open Inspector HUD
        inspectorTitle.innerText = data.title;
        inspectorTitle.style.color = data.color;
        inspectorSector.innerText = data.sector;
        inspectorFreq.innerText = data.frequency;
        inspectorEnergy.innerText = data.energy_signature;
        inspectorLore.innerText = data.lore;
        inspectorLore.style.borderLeftColor = data.color;
        if (oracleOutput) oracleOutput.style.display = "none";
        inspector.classList.remove("collapsed");

        // Cinematic camera fly-to
        const targetPos = group.position.clone();
        const offsetDist = isMobile ? 22 : 18;
        const offset = targetPos.clone().normalize().multiplyScalar(offsetDist);
        targetCameraPos = targetPos.clone().add(offset);
        targetCameraPos.y += isMobile ? 8 : 6;
        targetLookAt = targetPos;
    }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    /**
     * UI Action Handlers (Desktop & Mobile)
     */
    function setupUIControls() {
        // Mobile default: Collapse left controls on small screens
        if (isMobile && leftControls) {
            leftControls.classList.add("collapsed");
        }

        // Controls Toggle Button (Mobile & Desktop)
        const controlsToggleBtn = document.getElementById("controls-toggle-btn");
        if (controlsToggleBtn && leftControls) {
            controlsToggleBtn.addEventListener("click", () => {
                leftControls.classList.toggle("collapsed");
                const isNowOpen = !leftControls.classList.contains("collapsed");
                controlsToggleBtn.classList.toggle("active", isNowOpen);
                if (isNowOpen && inspector) {
                    inspector.classList.add("collapsed"); // Mutually exclusive on small screens
                }
            });
        }

        // Mobile Close Controls Button
        const closeControlsBtn = document.getElementById("close-controls-btn");
        if (closeControlsBtn && leftControls) {
            closeControlsBtn.addEventListener("click", () => {
                leftControls.classList.add("collapsed");
                if (controlsToggleBtn) controlsToggleBtn.classList.remove("active");
            });
        }

        // Audio Toggle
        const audioBtn = document.getElementById("audio-toggle-btn");
        if (audioBtn) {
            audioBtn.addEventListener("click", () => {
                const active = window.aetheriaAudio.toggle();
                audioBtn.classList.toggle("active", active);
                const iconSpan = audioBtn.querySelector(".btn-icon");
                const textSpan = audioBtn.querySelector(".btn-text");
                if (iconSpan) iconSpan.innerText = active ? "🔊" : "🔇";
                if (textSpan) textSpan.innerText = active ? " AUDIO: ON" : " AUDIO: OFF";
                showToast(active ? "Cosmic Soundscape Engaged" : "Soundscape Suspended");
            });
        }

        // Speed Slider
        const speedSlider = document.getElementById("speed-slider");
        const speedVal = document.getElementById("speed-val");
        if (speedSlider) {
            speedSlider.addEventListener("input", (e) => {
                speedMult = parseFloat(e.target.value);
                speedVal.innerText = speedMult.toFixed(1) + "x";
            });
        }

        // Gravity Slider
        const gravitySlider = document.getElementById("gravity-slider");
        const gravityVal = document.getElementById("gravity-val");
        if (gravitySlider) {
            gravitySlider.addEventListener("input", (e) => {
                gravityMult = parseFloat(e.target.value);
                gravityVal.innerText = gravityMult.toFixed(1) + "x";
            });
        }

        // Theme Pills
        document.querySelectorAll(".theme-pill").forEach(pill => {
            pill.addEventListener("click", () => {
                document.querySelectorAll(".theme-pill").forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                const theme = pill.dataset.theme;
                switchTheme(theme);
            });
        });

        // Warp Speed Button
        const warpBtn = document.getElementById("warp-btn");
        if (warpBtn) {
            warpBtn.addEventListener("click", () => {
                triggerWarpJump();
            });
        }

        // Reset Camera
        const resetCamBtn = document.getElementById("reset-cam-btn");
        if (resetCamBtn) {
            resetCamBtn.addEventListener("click", () => {
                targetCameraPos = new THREE.Vector3(0, isMobile ? 36 : 30, isMobile ? 96 : 85);
                targetLookAt = new THREE.Vector3(0, 0, 0);
                if (inspector) inspector.classList.add("collapsed");
                showToast("Orbital View Restored");
            });
        }

        // Close Inspector
        const closeInspectorBtn = document.getElementById("close-inspector-btn");
        if (closeInspectorBtn && inspector) {
            closeInspectorBtn.addEventListener("click", () => {
                inspector.classList.add("collapsed");
            });
        }

        // Oracle Question Transmission
        const oracleForm = document.getElementById("oracle-form");
        const oracleInput = document.getElementById("oracle-input");
        if (oracleForm && oracleInput) {
            oracleForm.addEventListener("submit", (e) => {
                e.preventDefault();
                const text = oracleInput.value.trim();
                if (!text) return;

                const anomalyName = selectedAnomaly ? selectedAnomaly.userData.title : "Cosmic Core";
                oracleOutput.style.display = "block";
                oracleOutput.innerText = "Transmitting to NVIDIA Nemotron Oracle across the quantum void...";

                if (window.aetheriaAudio) {
                    window.aetheriaAudio.playChime(3);
                }

                // Unfocus input on mobile to hide software keyboard
                oracleInput.blur();

                fetch("/api/transmit", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "ngrok-skip-browser-warning": "true"
                    },
                    body: jsonString({ prompt: text, anomaly: anomalyName })
                })
                .then(res => res.json())
                .then(data => {
                    oracleOutput.innerText = `"${data.response}"`;
                    if (window.aetheriaAudio) {
                        window.aetheriaAudio.playChime(6);
                    }
                })
                .catch(err => {
                    oracleOutput.innerText = "Cosmic flux disrupted: " + err.message;
                });
            });
        }

        // Screenshot capture button
        const snapshotBtn = document.getElementById("snapshot-btn");
        if (snapshotBtn) {
            snapshotBtn.addEventListener("click", () => {
                captureScreenshot();
            });
        }
    }

    function switchTheme(theme) {
        if (!PALETTES[theme]) return;
        activeTheme = theme;
        const pal = PALETTES[theme];

        scene.fog.color.setHex(pal.fog);
        renderer.setClearColor(pal.fog, 1);

        if (coreGroup) {
            coreGroup.children[0].material.color.setHex(pal.core);
            coreGroup.children[1].material.color.setHex(pal.ring);
            coreGroup.children[2].material.color.setHex(pal.ring);
            coreGroup.children[3].material.color.setHex(pal.ring);
        }

        if (window.aetheriaAudio) {
            window.aetheriaAudio.setMode(theme);
        }

        // Recolor particles
        createParticleUniverse(particlesCount);
        showToast(`Theme Attuned: ${theme.toUpperCase()}`);
    }

    function triggerWarpJump() {
        if (isWarping) return;
        isWarping = true;
        showToast("WARP JUMP INITIATED");

        if (window.aetheriaAudio) {
            window.aetheriaAudio.playWarpSound();
        }

        let start = performance.now();
        let duration = 2200;

        function warpStep(now) {
            let elapsed = now - start;
            let progress = elapsed / duration;

            if (progress < 0.5) {
                warpFactor = 1.0 + (progress * 2) * 12.0; // Accelerate to 13x
            } else if (progress < 1.0) {
                warpFactor = 13.0 - ((progress - 0.5) * 2) * 12.0; // Decelerate
            } else {
                warpFactor = 1.0;
                isWarping = false;
                // Randomize camera angle after jump
                const angle = Math.random() * Math.PI * 2;
                targetCameraPos = new THREE.Vector3(Math.cos(angle) * 80, 25 + Math.random() * 20, Math.sin(angle) * 80);
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

    /**
     * Main Animation & Render Loop (60+ FPS)
     */
    function animate(time) {
        requestAnimationFrame(animate);

        // FPS calculation
        frameCount++;
        if (time - lastTime >= 1000) {
            fps = Math.round((frameCount * 1000) / (time - lastTime));
            if (fpsVal) fpsVal.innerText = fps + " FPS";
            frameCount = 0;
            lastTime = time;
        }

        const effSpeed = speedMult * warpFactor;
        const audioEnergy = window.aetheriaAudio ? window.aetheriaAudio.getEnergy() : 0;

        // 1. Rotate Central Core
        if (coreGroup) {
            coreGroup.rotation.y += 0.005 * effSpeed;
            coreGroup.rotation.x += 0.002 * effSpeed;

            // Pulse with audio energy
            const scale = 1.0 + (audioEnergy * 0.45);
            coreGroup.scale.set(scale, scale, scale);
        }

        // 2. Animate Anomaly Beacons
        anomalies.forEach((grp) => {
            const d = grp.userData;
            // Orbit central pulsar
            const angle = time * d.orbitSpeed * 0.001 * effSpeed;
            grp.position.x = Math.cos(angle) * d.basePos.x - Math.sin(angle) * d.basePos.z;
            grp.position.z = Math.sin(angle) * d.basePos.x + Math.cos(angle) * d.basePos.z;
            grp.position.y = d.basePos.y + Math.sin(time * 0.002) * 1.5;

            // Rotate individual beacon meshes
            d.mesh.rotation.y += 0.02 * effSpeed;
            d.mesh.rotation.x += 0.015 * effSpeed;
            d.halo.rotation.z -= 0.01 * effSpeed;
        });

        // 3. Update Particle Positions with Keplerian Physics
        if (particleGeometry && particlePositions) {
            const pos = particlePositions;
            const vel = particleVelocities;
            const count = particlesCount;

            for (let i = 0; i < count; i++) {
                const i3 = i * 3;
                let px = pos[i3];
                let py = pos[i3 + 1];
                let pz = pos[i3 + 2];

                // Orbital drift
                px += vel[i3] * effSpeed;
                py += vel[i3 + 1] * effSpeed;
                pz += vel[i3 + 2] * effSpeed;

                // Central gravity pull
                const distSq = px * px + py * py + pz * pz;
                if (distSq > 100) {
                    const pull = (0.04 * gravityMult) / Math.sqrt(distSq);
                    vel[i3] -= (px / Math.sqrt(distSq)) * pull;
                    vel[i3 + 2] -= (pz / Math.sqrt(distSq)) * pull;
                }

                // Warp elongation
                if (isWarping) {
                    pz += vel[i3 + 2] * (warpFactor * 2.5);
                }

                // Bounds wrap
                if (distSq > 35000) {
                    px *= 0.2;
                    pz *= 0.2;
                }

                pos[i3] = px;
                pos[i3 + 1] = py;
                pos[i3 + 2] = pz;
            }
            particleGeometry.attributes.position.needsUpdate = true;
        }

        // 4. Smooth Camera Interpolation for Fly-To
        if (targetCameraPos) {
            camera.position.lerp(targetCameraPos, 0.045);
            currentLookAt.lerp(targetLookAt, 0.045);
            controls.target.copy(currentLookAt);
            if (camera.position.distanceTo(targetCameraPos) < 0.2) {
                targetCameraPos = null;
            }
        }

        controls.update();
        renderer.render(scene, camera);
    }

    // Initialize on DOM Ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

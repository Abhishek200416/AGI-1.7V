/**
 * AETHERIA 3D • Generative Web Audio Synthesizer Engine (Mobile & Desktop)
 * =============================================================================
 * Pure Web Audio API procedural synthesizer.
 * Creates evolving celestial drones, interactive crystalline chimes, and
 * real-time frequency data for 3D visual reactivity with zero audio file assets.
 * Optimized with touch-gesture unlocks for mobile Safari and Chrome.
 * =============================================================================
 */

class AetheriaAudioEngine {
    constructor() {
        this.ctx = null;
        this.masterGain = null;
        this.analyser = null;
        this.isPlaying = false;
        this.volume = 0.5;
        this.droneOscillators = [];
        this.lfo = null;
        this.filter = null;
        this.currentMode = "zen";

        // Frequency scales for harmonic chimes (Pentatonic & Cosmic Intervals)
        this.scales = {
            zen: [216.0, 256.8, 288.0, 324.0, 384.0, 432.0, 513.6, 576.0, 648.0, 864.0],
            cyber: [220.0, 261.6, 293.6, 329.6, 392.0, 440.0, 523.2, 587.3, 659.2, 880.0],
            solar: [261.6, 294.3, 327.0, 392.4, 436.0, 523.2, 588.6, 654.0, 784.8, 1046.4],
            void: [108.0, 135.0, 162.0, 216.0, 270.0, 324.0, 432.0, 540.0, 648.0, 864.0]
        };
    }

    init() {
        if (this.ctx) return;
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();

        // Master Gain
        this.masterGain = this.ctx.createGain();
        this.masterGain.gain.setValueAtTime(this.volume, this.ctx.currentTime);

        // Analyser node for 3D visual reactivity
        this.analyser = this.ctx.createAnalyser();
        this.analyser.fftSize = 64;
        this.analyser.smoothingTimeConstant = 0.8;

        this.masterGain.connect(this.analyser);
        this.analyser.connect(this.ctx.destination);
    }

    startDrone(mode = "zen") {
        this.init();
        if (this.ctx.state === "suspended") {
            this.ctx.resume();
        }
        if (this.isPlaying) {
            this.stopDrone();
        }

        this.currentMode = mode;
        const now = this.ctx.currentTime;

        // Lowpass Filter with resonance
        this.filter = this.ctx.createBiquadFilter();
        this.filter.type = "lowpass";
        this.filter.frequency.setValueAtTime(450, now);
        this.filter.Q.setValueAtTime(3.5, now);

        // Slow LFO for filter breathing
        this.lfo = this.ctx.createOscillator();
        this.lfo.frequency.setValueAtTime(0.12, now); // ~8 second breathing cycle
        const lfoGain = this.ctx.createGain();
        lfoGain.gain.setValueAtTime(220, now);
        this.lfo.connect(lfoGain);
        lfoGain.connect(this.filter.frequency);
        this.lfo.start();

        // Base drone root frequencies
        let roots = [108, 162, 216, 324]; // 432 Hz Pythagorean Sub-harmonics
        if (mode === "cyber") roots = [110, 164.8, 220, 329.6];
        else if (mode === "solar") roots = [130.8, 196.2, 261.6, 392.4];
        else if (mode === "void") roots = [54, 81, 108, 162];

        this.droneOscillators = [];
        roots.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = idx % 2 === 0 ? "sine" : "triangle";
            osc.frequency.setValueAtTime(freq, now);

            // Subtle random detuning for organic chorus warmth
            osc.detune.setValueAtTime((Math.random() - 0.5) * 8, now);

            // Level per voice
            const voiceLevel = 0.18 / (idx + 1);
            gain.gain.setValueAtTime(0.001, now);
            gain.gain.exponentialRampToValueAtTime(voiceLevel, now + 3.0); // Gentle fade in

            osc.connect(gain);
            gain.connect(this.filter);
            osc.start();

            this.droneOscillators.push({ osc, gain });
        });

        this.filter.connect(this.masterGain);
        this.isPlaying = true;
    }

    stopDrone() {
        if (!this.isPlaying || !this.ctx) return;
        const now = this.ctx.currentTime;
        this.droneOscillators.forEach(({ osc, gain }) => {
            try {
                gain.gain.linearRampToValueAtTime(0.0001, now + 1.0);
                osc.stop(now + 1.1);
            } catch (e) {}
        });
        if (this.lfo) {
            try { this.lfo.stop(now + 1.1); } catch (e) {}
        }
        this.droneOscillators = [];
        this.isPlaying = false;
    }

    toggle() {
        if (this.isPlaying) {
            this.stopDrone();
            return false;
        } else {
            this.startDrone(this.currentMode);
            return true;
        }
    }

    setVolume(val) {
        this.volume = Math.max(0, Math.min(1, val));
        if (this.masterGain && this.ctx) {
            this.masterGain.gain.setValueAtTime(this.volume, this.ctx.currentTime);
        }
    }

    setMode(mode) {
        this.currentMode = mode;
        if (this.isPlaying) {
            this.startDrone(mode);
        }
    }

    /**
     * Plays a celestial bell chime tuned to the current harmonic scale.
     */
    playChime(noteIndex = null, customFreq = null) {
        this.init();
        if (this.ctx.state === "suspended") {
            this.ctx.resume();
        }

        const now = this.ctx.currentTime;
        const scale = this.scales[this.currentMode] || this.scales.zen;
        let freq = customFreq;

        if (!freq) {
            const idx = noteIndex !== null ? noteIndex % scale.length : Math.floor(Math.random() * scale.length);
            freq = scale[idx];
        }

        // Two oscillators for crystalline bell overtone
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const chimeGain = this.ctx.createGain();

        osc1.type = "sine";
        osc1.frequency.setValueAtTime(freq, now);

        osc2.type = "triangle";
        osc2.frequency.setValueAtTime(freq * 2.756, now); // Metallic celestial overtone
        osc2.detune.setValueAtTime(4, now);

        // Percussive bell envelope
        chimeGain.gain.setValueAtTime(0.001, now);
        chimeGain.gain.linearRampToValueAtTime(0.35 * this.volume, now + 0.02);
        chimeGain.gain.exponentialRampToValueAtTime(0.0001, now + 2.5);

        osc1.connect(chimeGain);
        osc2.connect(chimeGain);
        chimeGain.connect(this.masterGain);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 2.6);
        osc2.stop(now + 2.6);
    }

    /**
     * Warp speed audio sweep effect for hyperspace jumps.
     */
    playWarpSound() {
        this.init();
        if (this.ctx.state === "suspended") this.ctx.resume();

        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(80, now);
        osc.frequency.exponentialRampToValueAtTime(880, now + 1.2);
        osc.frequency.exponentialRampToValueAtTime(120, now + 2.2);

        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.4 * this.volume, now + 0.8);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 2.4);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start(now);
        osc.stop(now + 2.5);
    }

    /**
     * Gets instantaneous frequency energy (0.0 to 1.0) for visual reactivity.
     */
    getEnergy() {
        if (!this.analyser || !this.isPlaying) return 0;
        const data = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
            sum += data[i];
        }
        return (sum / (data.length * 255));
    }
}

window.aetheriaAudio = new AetheriaAudioEngine();

// Mobile audio unlocking on first user touch gesture
const unlockAudioContext = () => {
    if (window.aetheriaAudio) {
        window.aetheriaAudio.init();
        if (window.aetheriaAudio.ctx && window.aetheriaAudio.ctx.state === "suspended") {
            window.aetheriaAudio.ctx.resume();
        }
    }
};
window.addEventListener("touchstart", unlockAudioContext, { once: true, passive: true });
window.addEventListener("click", unlockAudioContext, { once: true });

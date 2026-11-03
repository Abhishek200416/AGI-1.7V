/**
 * Native Web Audio API Synthesizer for IVA 3D Observatory.
 * Generates interactive ambient drone frequencies and crystal resonant tones.
 * Zero external libraries or audio files required.
 */

class NeuralAudioSynthesizer {
    constructor() {
        this.ctx = null;
        this.isEnabled = false;
        this.masterGain = null;
        this.droneOsc = null;
    }

    init() {
        if (this.ctx) return;
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContext();
            this.masterGain = this.ctx.createGain();
            this.masterGain.gain.setValueAtTime(0.08, this.ctx.currentTime);
            this.masterGain.connect(this.ctx.destination);
            this.isEnabled = true;
            this.startAmbientDrone();
        } catch (e) {
            console.warn("Web Audio API not supported in this browser:", e);
        }
    }

    startAmbientDrone() {
        if (!this.ctx || !this.isEnabled) return;
        // Deep 55Hz ambient resonant frequency
        this.droneOsc = this.ctx.createOscillator();
        const droneGain = this.ctx.createGain();
        this.droneOsc.type = 'sine';
        this.droneOsc.frequency.setValueAtTime(55, this.ctx.currentTime);

        droneGain.gain.setValueAtTime(0.02, this.ctx.currentTime);
        this.droneOsc.connect(droneGain);
        droneGain.connect(this.masterGain);
        this.droneOsc.start();
    }

    playNodeHover(frequency = 440) {
        if (!this.ctx || !this.isEnabled) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(frequency, this.ctx.currentTime);

        gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.15);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.15);
    }

    playNodeSelect(frequency = 880) {
        if (!this.ctx || !this.isEnabled) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(frequency, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(frequency * 1.5, this.ctx.currentTime + 0.3);

        gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.35);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.35);
    }

    toggle() {
        if (!this.ctx) {
            this.init();
            return true;
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
            this.isEnabled = true;
            return true;
        } else if (this.ctx.state === 'running') {
            this.ctx.suspend();
            this.isEnabled = false;
            return false;
        }
        return false;
    }
}

window.neuralAudio = new NeuralAudioSynthesizer();

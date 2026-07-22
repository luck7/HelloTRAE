let audioCtx: AudioContext | null = null;

export function getAudioCtx(): AudioContext {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    return audioCtx;
}

export function playExplosionSound(isSteel: boolean = false): void {
    const ctx: AudioContext = getAudioCtx();
    const now: number = ctx.currentTime;
    const bufferSize: number = ctx.sampleRate * 0.15;
    const buffer: AudioBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data: Float32Array = buffer.getChannelData(0);
    for (let i: number = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 2);
    }
    const noise: AudioBufferSourceNode = ctx.createBufferSource();
    noise.buffer = buffer;
    const gain: GainNode = ctx.createGain();
    gain.gain.setValueAtTime(isSteel ? 0.15 : 0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
    const filter: BiquadFilterNode = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(isSteel ? 2000 : 800, now);
    noise.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    noise.start(now);
    noise.stop(now + 0.15);
}

export function playTankExplosionSound(): void {
    const ctx: AudioContext = getAudioCtx();
    const now: number = ctx.currentTime;
    const bufferSize: number = ctx.sampleRate * 0.4;
    const buffer: AudioBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data: Float32Array = buffer.getChannelData(0);
    for (let i: number = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 1.5);
    }
    const noise: AudioBufferSourceNode = ctx.createBufferSource();
    noise.buffer = buffer;
    const gain: GainNode = ctx.createGain();
    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
    const filter: BiquadFilterNode = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(600, now);
    noise.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    noise.start(now);
    noise.stop(now + 0.4);

    const osc: OscillatorNode = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(80, now);
    osc.frequency.exponentialRampToValueAtTime(30, now + 0.3);
    const oscGain: GainNode = ctx.createGain();
    oscGain.gain.setValueAtTime(0.2, now);
    oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
    osc.connect(oscGain);
    oscGain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.3);
}

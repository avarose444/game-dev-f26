// After Hours ambience, made entirely with the Web Audio API (no audio files, nothing to license).
// Layers: rain (always), neon hum (always), lounge piano (close at the Lantern, distant elsewhere),
// rooftop wind, clinic monitor beep. Plus one-shot effects for game moments.
// Browsers only allow audio after a click, so Sound.start() is called from the phone's button.

const Sound = (() => {
  let ctx = null, master = null, layers = {}, pianoTimer = null, beepTimer = null, muted = false, place = "street";
  try { muted = localStorage.getItem("ah-muted") === "1"; } catch (e) { /* storage may be blocked */ }

  function noiseBuffer(seconds = 2) {
    const buf = ctx.createBuffer(1, ctx.sampleRate * seconds, ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
    return buf;
  }
  function noiseSource() {
    const src = ctx.createBufferSource();
    src.buffer = noiseBuffer(); src.loop = true; src.start();
    return src;
  }
  function gainNode(value, dest = master) {
    const g = ctx.createGain(); g.gain.value = value; g.connect(dest); return g;
  }
  function fade(g, value, seconds = 1.5) {
    if (g) g.gain.setTargetAtTime(value, ctx.currentTime, seconds / 3);
  }

  function buildRain() {
    const g = gainNode(0.0);
    const band = ctx.createBiquadFilter(); band.type = "bandpass"; band.frequency.value = 1400; band.Q.value = 0.6;
    const hp = ctx.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 500;
    noiseSource().connect(band); band.connect(hp); hp.connect(g);
    const rumble = gainNode(0.0);
    const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 180;
    noiseSource().connect(lp); lp.connect(rumble);
    return { g, rumble };
  }

  function buildHum() {
    const g = gainNode(0.0);
    const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 380;
    const osc = ctx.createOscillator(); osc.type = "sawtooth"; osc.frequency.value = 120;
    osc.connect(lp); lp.connect(g); osc.start();
    return g;
  }

  function buildWind() {
    const g = gainNode(0.0);
    const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 420; lp.Q.value = 4;
    const lfo = ctx.createOscillator(); lfo.frequency.value = 0.08;
    const depth = ctx.createGain(); depth.gain.value = 260;
    lfo.connect(depth); depth.connect(lp.frequency); lfo.start();
    noiseSource().connect(lp); lp.connect(g);
    return g;
  }

  // A small "room": feedback delay, darkened, so the piano sounds like it's in another room.
  function buildRoom(dest) {
    const input = ctx.createGain();
    const delay = ctx.createDelay(1); delay.delayTime.value = 0.31;
    const fb = ctx.createGain(); fb.gain.value = 0.38;
    const tone = ctx.createBiquadFilter(); tone.type = "lowpass"; tone.frequency.value = 1800;
    input.connect(dest); input.connect(delay); delay.connect(tone); tone.connect(fb); fb.connect(delay); tone.connect(dest);
    return input;
  }

  // Jazz-lounge voicings (Dm9, G13, Cmaj9, A7b9), played as soft broken chords.
  const CHORDS = [[50, 53, 57, 60, 64], [43, 53, 57, 59, 64], [48, 52, 55, 59, 62], [45, 49, 52, 55, 58]];
  let chordIndex = 0;
  const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
  function pianoNote(midi, when, velocity) {
    const g = ctx.createGain();
    g.gain.setValueAtTime(0, when);
    g.gain.linearRampToValueAtTime(velocity, when + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, when + 3.2);
    g.connect(layers.pianoRoom);
    for (const [type, mult, amt] of [["triangle", 1, 1], ["sine", 2, 0.35], ["sine", 3, 0.12]]) {
      const o = ctx.createOscillator(); o.type = type; o.frequency.value = mtof(midi) * mult;
      const og = ctx.createGain(); og.gain.value = amt; o.connect(og); og.connect(g);
      o.start(when); o.stop(when + 3.3);
    }
  }
  function playChord() {
    const chord = CHORDS[chordIndex++ % CHORDS.length];
    const t = ctx.currentTime + 0.05;
    chord.forEach((m, i) => pianoNote(m, t + i * (0.09 + Math.random() * 0.06), 0.05 + Math.random() * 0.025));
    if (Math.random() < 0.5) pianoNote(chord[chord.length - 1] + 12, t + 1.1 + Math.random() * 0.4, 0.035);
    pianoTimer = setTimeout(playChord, 2600 + Math.random() * 2600);
  }

  function beep() {
    if (place === "clinic") {
      const t = ctx.currentTime;
      const o = ctx.createOscillator(); o.type = "sine"; o.frequency.value = 988;
      const g = gainNode(0); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.025, t + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.18);
      o.connect(g); o.start(t); o.stop(t + 0.2);
    }
    beepTimer = setTimeout(beep, 1900);
  }

  const MIX = {   // gain per layer for each place
    street:  { rain: 0.07, rumble: 0.05, hum: 0.008, piano: 0.25, wind: 0.0 },
    lantern: { rain: 0.025, rumble: 0.03, hum: 0.014, piano: 1.0, wind: 0.0 },
    rooftop: { rain: 0.09, rumble: 0.06, hum: 0.004, piano: 0.12, wind: 0.07 },
    clinic:  { rain: 0.05, rumble: 0.04, hum: 0.02, piano: 0.18, wind: 0.0 },
    lift:    { rain: 0.015, rumble: 0.07, hum: 0.0, piano: 0.0, wind: 0.02 },
    dawn:    { rain: 0.02, rumble: 0.02, hum: 0.0, piano: 0.6, wind: 0.0 },
  };

  function applyMix(seconds = 2) {
    if (!ctx) return;
    const m = MIX[place] || MIX.street;
    fade(layers.rain.g, m.rain, seconds); fade(layers.rain.rumble, m.rumble, seconds);
    fade(layers.hum, m.hum, seconds); fade(layers.piano, m.piano, seconds); fade(layers.wind, m.wind, seconds);
  }

  function start() {
    if (ctx) { if (ctx.state === "suspended") ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    ctx = new AC();
    master = ctx.createGain(); master.gain.value = muted ? 0 : 0.8; master.connect(ctx.destination);
    layers.rain = buildRain();
    layers.hum = buildHum();
    layers.wind = buildWind();
    layers.piano = gainNode(0);
    layers.pianoRoom = buildRoom(layers.piano);
    playChord(); beep(); applyMix(3);
    // The neon sign flickers; so does its hum.
    setInterval(() => {
      if (Math.random() < 0.25 && layers.hum) {
        const t = ctx.currentTime, base = (MIX[place] || MIX.street).hum;
        layers.hum.gain.setValueAtTime(base * 0.2, t); layers.hum.gain.setValueAtTime(base, t + 0.08 + Math.random() * 0.1);
      }
    }, 3000);
  }

  function setPlace(p) { place = p; applyMix(); }

  function setMuted(m) {
    muted = m;
    try { localStorage.setItem("ah-muted", m ? "1" : "0"); } catch (e) { /* ignore */ }
    if (master) master.gain.setTargetAtTime(m ? 0 : 0.8, ctx.currentTime, 0.2);
  }

  function tone(freq, start, dur, type = "sine", vol = 0.08, dest = master) {
    const o = ctx.createOscillator(); o.type = type; o.frequency.value = freq;
    const g = ctx.createGain(); g.gain.setValueAtTime(0, start);
    g.gain.linearRampToValueAtTime(vol, start + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    o.connect(g); g.connect(dest); o.start(start); o.stop(start + dur + 0.05);
    return o;
  }

  const sfx = {
    clue() { const t = ctx.currentTime; tone(1318.5, t, 1.6, "sine", 0.06); tone(1760, t + 0.12, 1.8, "sine", 0.05); tone(2637, t + 0.24, 1.2, "sine", 0.02); },
    deal() { const t = ctx.currentTime; tone(196, t, 0.9, "triangle", 0.07); tone(293.7, t + 0.08, 1.0, "triangle", 0.05); tone(392, t + 0.16, 1.2, "sine", 0.04); },
    hunt() {
      const t = ctx.currentTime;
      for (const off of [0, 0.32]) {
        const o = tone(70, t + off, 0.45, "sine", 0.22);
        o.frequency.setValueAtTime(90, t + off); o.frequency.exponentialRampToValueAtTime(42, t + off + 0.35);
      }
    },
    buzz() { const t = ctx.currentTime; for (const off of [0, 0.22]) tone(150, t + off, 0.14, "square", 0.025); },
    ending() { const t = ctx.currentTime; [48, 55, 59, 62, 67].forEach((m, i) => tone(mtof(m), t + i * 0.15, 5, "triangle", 0.035)); },
    step() { const t = ctx.currentTime; tone(220, t, 0.25, "sine", 0.03); },
  };

  function play(name) { if (ctx && !muted && sfx[name]) sfx[name](); }

  return { start, setPlace, setMuted, play, get muted() { return muted; }, get started() { return !!ctx; } };
})();

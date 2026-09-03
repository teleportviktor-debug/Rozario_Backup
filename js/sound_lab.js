// ====================================================
// PROCEDURAL SOUND LAB ENGINE (Web Audio API)
// ====================================================
let audioCtx = null;
let masterGain = null;
let biquadFilter = null;
let analyser = null;
let dataArray = null;
let canvasCtx = null;
let isSoundOn = false;

const slCutoff = document.getElementById('sl-cutoff');
const slRes = document.getElementById('sl-res');
const lblCutoff = document.getElementById('lbl-cutoff');
const lblRes = document.getElementById('lbl-res');
const typeBtns = document.querySelectorAll('#view-soundlab .type-btn');
const canvas = document.getElementById('oscilloscope');
const cockpit = document.getElementById('tilt-cockpit');
const cockpitWrapper = document.querySelector('.cockpit-wrapper');

function initSoundLab() {
  if (audioCtx) {
    if(audioCtx.state === 'suspended') audioCtx.resume();
    return;
  }
  
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  
  biquadFilter = audioCtx.createBiquadFilter();
  biquadFilter.type = 'lowpass';
  if (slCutoff) biquadFilter.frequency.value = parseInt(slCutoff.value);
  if (slRes) biquadFilter.Q.value = parseFloat(slRes.value);

  masterGain = audioCtx.createGain();
  masterGain.gain.value = 0.5;

  analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  
  const bufferLength = analyser.frequencyBinCount;
  dataArray = new Uint8Array(bufferLength);

  biquadFilter.connect(masterGain);
  masterGain.connect(analyser);
  analyser.connect(audioCtx.destination);

  if (canvas) {
    canvasCtx = canvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    drawOscilloscope();
  }
  
  isSoundOn = true;
  document.getElementById('btn-sound-lab').innerText = "Аудио Движок АКТИВЕН 🔊";
  document.getElementById('btn-sound-lab').classList.add('btn-indigo');
}

function drawOscilloscope() {
  requestAnimationFrame(drawOscilloscope);
  if(!analyser || !canvasCtx) return;

  analyser.getByteTimeDomainData(dataArray);

  canvasCtx.fillStyle = 'rgba(0, 0, 0, 0.3)';
  canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

  canvasCtx.lineWidth = 2;
  canvasCtx.strokeStyle = '#00F2FE';
  canvasCtx.beginPath();

  const sliceWidth = canvas.width * 1.0 / dataArray.length;
  let x = 0;

  for(let i = 0; i < dataArray.length; i++) {
    const v = dataArray[i] / 128.0;
    const y = v * canvas.height / 2;
    if(i === 0) canvasCtx.moveTo(x, y);
    else canvasCtx.lineTo(x, y);
    x += sliceWidth;
  }
  canvasCtx.lineTo(canvas.width, canvas.height / 2);
  canvasCtx.stroke();
}

function resizeCanvas() {
  if (!canvas) return;
  canvas.width = canvas.parentElement.clientWidth - 40;
  canvas.height = 200;
}

function playOscillatorLab(type, freq, duration, volMod = 1, volDecay = true) {
  if(!isSoundOn || !audioCtx) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
  gain.gain.setValueAtTime(volMod, audioCtx.currentTime);
  if(volDecay) gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
  osc.connect(gain);
  gain.connect(biquadFilter); 
  osc.start();
  osc.stop(audioCtx.currentTime + duration);
}

// BINDINGS
if (slCutoff) {
  slCutoff.addEventListener('input', (e) => {
    lblCutoff.innerText = e.target.value + ' Hz';
    if(biquadFilter) biquadFilter.frequency.setValueAtTime(e.target.value, audioCtx.currentTime);
    playOscillatorLab('sine', 800, 0.05, 0.1);
  });
}
if (slRes) {
  slRes.addEventListener('input', (e) => {
    lblRes.innerText = e.target.value;
    if(biquadFilter) biquadFilter.Q.setValueAtTime(e.target.value, audioCtx.currentTime);
    playOscillatorLab('sine', 800, 0.05, 0.1);
  });
}

typeBtns.forEach(btn => {
  btn.addEventListener('click', (e) => {
    typeBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if(biquadFilter) biquadFilter.type = btn.getAttribute('data-type');
    playOscillatorLab('square', 1200, 0.05, 0.1);
  });
});

document.getElementById('pad-hover')?.addEventListener('mousedown', () => playOscillatorLab('sine', 800, 0.1, 0.2));
document.getElementById('pad-click')?.addEventListener('mousedown', () => playOscillatorLab('square', 1200, 0.05, 0.3));
document.getElementById('pad-toggle')?.addEventListener('mousedown', () => {
  if(!isSoundOn || !audioCtx) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(300, audioCtx.currentTime);
  osc.frequency.setValueAtTime(600, audioCtx.currentTime + 0.05);
  gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
  osc.connect(gain);
  gain.connect(biquadFilter);
  osc.start();
  osc.stop(audioCtx.currentTime + 0.15);
});
document.getElementById('pad-success')?.addEventListener('mousedown', () => {
  if(!isSoundOn || !audioCtx) return;
  const freqs = [440, 554.37, 659.25, 880];
  freqs.forEach((freq, i) => {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime + (i * 0.05));
    gain.gain.setValueAtTime(0.2, audioCtx.currentTime + (i * 0.05));
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + (i * 0.05) + 0.5);
    osc.connect(gain);
    gain.connect(biquadFilter);
    osc.start(audioCtx.currentTime + (i * 0.05));
    osc.stop(audioCtx.currentTime + (i * 0.05) + 0.5);
  });
});

if (cockpitWrapper && cockpit) {
  cockpitWrapper.addEventListener('mousemove', (e) => {
    const rect = cockpitWrapper.getBoundingClientRect();
    const x = e.clientX - rect.left; 
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -5;
    const rotateY = ((x - centerX) / centerX) * 5;
    cockpit.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  });
  cockpitWrapper.addEventListener('mouseleave', () => { cockpit.style.transform = `rotateX(0deg) rotateY(0deg)`; });
}

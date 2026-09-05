"""
Audio Designer (Agent 3 - Audio Engineer & Orchestrator)
Architecture "Genome" - Razum Google AI PRO.

Three-layer Sound Design Engine:
1. Layer 1 (Voiceover): Deep confident baritone (neural TTS via edge-tts or procedural).
2. Layer 2 (UI SFX): Tactile procedural sound library (mechanical typing, haptic pops, air whooshes).
3. Layer 3 (BGM): Minimalist cyber tech beat with automated sidechain ducking (-14dB during voice).
"""

import os
import sys
import wave
import math
import struct
import shutil
import asyncio
import subprocess
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def get_ffmpeg_executable() -> str:
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(exe):
            return exe
    except Exception:
        pass
    path_exe = shutil.which("ffmpeg")
    if path_exe:
        return path_exe
    raise RuntimeError("FFmpeg executable not found.")


class AudioDesigner:
    """
    Manages procedural sound synthesis, voiceover generation, and FFmpeg 3-layer audio mixing
    with sidechain compression.
    """

    def __init__(self, output_dir: Optional[str] = None, sample_rate: int = 44100):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.output_dir = output_dir or os.path.join(base_dir, "output", "audio_library")
        os.makedirs(self.output_dir, exist_ok=True)
        self.sample_rate = sample_rate
        self.ffmpeg_exe = get_ffmpeg_executable()

    def _save_wav(self, filepath: str, samples: np.ndarray):
        """Saves a 1D float numpy array (-1.0 to 1.0) as 16-bit PCM WAV."""
        samples = np.clip(samples, -1.0, 1.0)
        int_samples = (samples * 32767.0).astype(np.int16)
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(int_samples.tobytes())

    # --- Layer 2: UI SFX Generators ---

    def generate_click_sfx(self, filepath: Optional[str] = None) -> str:
        """
        Generates a crisp tactile haptic click / pop for card reveals.
        Damped sine wave + subtle noise burst with exponential decay.
        """
        out_path = filepath or os.path.join(self.output_dir, "click.wav")
        duration = 0.045
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        decay = np.exp(-t * 220.0)
        # 1600 Hz tone with pitch envelope drop
        freq = 1600.0 * np.exp(-t * 80.0)
        tone = np.sin(2.0 * np.pi * freq * t)
        noise = np.random.uniform(-0.3, 0.3, len(t))
        samples = (0.75 * tone + 0.25 * noise) * decay
        self._save_wav(out_path, samples)
        return out_path

    def generate_type_sfx(self, filepath: Optional[str] = None) -> str:
        """
        Generates a mechanical keyboard keypress click for the prompt typing hook.
        Short crisp transient.
        """
        out_path = filepath or os.path.join(self.output_dir, "type.wav")
        duration = 0.028
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        decay = np.exp(-t * 320.0)
        tone = np.sin(2.0 * np.pi * 2400.0 * t)
        noise = np.random.uniform(-0.5, 0.5, len(t))
        samples = (0.5 * tone + 0.5 * noise) * decay
        self._save_wav(out_path, samples)
        return out_path

    def generate_whoosh_sfx(self, filepath: Optional[str] = None) -> str:
        """
        Generates a smooth subtle air whoosh for scene transitions.
        Frequency-swept noise with a bell-shaped amplitude envelope.
        """
        out_path = filepath or os.path.join(self.output_dir, "whoosh.wav")
        duration = 0.38
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        # Bell curve envelope
        env = np.sin(np.pi * t / duration) ** 2
        noise = np.random.uniform(-0.6, 0.6, len(t))
        # Swept sub tone from 500Hz down to 180Hz
        sweep_freq = 500.0 - 320.0 * (t / duration)
        sweep_tone = np.sin(2.0 * np.pi * sweep_freq * t)
        samples = (0.6 * noise + 0.4 * sweep_tone) * env * 0.7
        self._save_wav(out_path, samples)
        return out_path

    # --- Layer 3: Minimalist Cyber Tech BGM Generator ---

    def generate_bgm_track(self, duration_sec: float = 15.0, bpm: float = 120.0, filepath: Optional[str] = None) -> str:
        """
        Synthesizes a sleek, low-key cyber dark tech beat (120 BPM):
        - Sub-bass pulses (55Hz / 110Hz A1 notes)
        - Crisp hi-hat ticks on 8th notes
        - Atmospheric dark ambient pad chord drone
        """
        out_path = filepath or os.path.join(self.output_dir, "bgm.wav")
        total_samples = int(self.sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, total_samples, endpoint=False)
        mix = np.zeros(total_samples, dtype=np.float32)

        # 1. Atmospheric dark drone pad (A minor root: 110Hz, 164.81Hz, 220Hz)
        pad = (
            0.12 * np.sin(2.0 * np.pi * 110.0 * t) +
            0.08 * np.sin(2.0 * np.pi * 164.81 * t + 0.5) +
            0.06 * np.sin(2.0 * np.pi * 220.0 * t + 1.0)
        )
        # Slow filter swell LFO
        lfo = 0.7 + 0.3 * np.sin(2.0 * np.pi * 0.2 * t)
        mix += pad * lfo

        # 2. Sub-bass kick pulses on quarter notes (every 0.5s)
        beat_interval = 60.0 / bpm  # 0.5 sec
        sub_samples_count = int(self.sample_rate * 0.3)
        sub_t = np.linspace(0, 0.3, sub_samples_count, endpoint=False)
        sub_kick = np.sin(2.0 * np.pi * (55.0 * np.exp(-sub_t * 8.0)) * sub_t) * np.exp(-sub_t * 12.0)

        # 3. Hi-hat ticks on eighth notes (every 0.25s)
        hat_samples_count = int(self.sample_rate * 0.04)
        hat_t = np.linspace(0, 0.04, hat_samples_count, endpoint=False)
        hat = np.random.uniform(-0.15, 0.15, hat_samples_count) * np.exp(-hat_t * 120.0)

        num_beats = int(duration_sec / beat_interval)
        for b in range(num_beats):
            start_idx = int(b * beat_interval * self.sample_rate)
            # Kick on beats
            end_kick = min(total_samples, start_idx + len(sub_kick))
            mix[start_idx:end_kick] += sub_kick[:end_kick - start_idx] * 0.45

            # Hi-hat on 8th notes
            hat_start_1 = start_idx
            end_hat_1 = min(total_samples, hat_start_1 + len(hat))
            mix[hat_start_1:end_hat_1] += hat[:end_hat_1 - hat_start_1] * 0.25

            hat_start_2 = start_idx + int(beat_interval * 0.5 * self.sample_rate)
            if hat_start_2 < total_samples:
                end_hat_2 = min(total_samples, hat_start_2 + len(hat))
                mix[hat_start_2:end_hat_2] += hat[:end_hat_2 - hat_start_2] * 0.18

        # Master normalize to -6dB peak (0.5 max)
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = (mix / peak) * 0.55

        self._save_wav(out_path, mix)
        return out_path

    # --- Layer 1: Neural Baritone Voiceover Generator ---

    async def _synthesize_neural_voice(self, script: str, out_mp3: str):
        import edge_tts
        # Deep confident baritone voice: en-US-ChristopherNeural with pitch drop and clear cadence
        communicate = edge_tts.Communicate(
            text=script,
            voice="en-US-ChristopherNeural",
            pitch="-6Hz",
            rate="+3%"
        )
        await communicate.save(out_mp3)

    def generate_voiceover_track(
        self,
        script: str,
        duration_sec: float = 15.0,
        filepath: Optional[str] = None
    ) -> str:
        """
        Generates deep baritone voiceover via neural TTS.
        Converts to WAV and pads / normalizes to target duration.
        """
        out_wav = filepath or os.path.join(self.output_dir, "voiceover.wav")
        temp_mp3 = os.path.join(self.output_dir, "temp_voice.mp3")

        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(lambda: asyncio.run(self._synthesize_neural_voice(script, temp_mp3))).result()
            else:
                asyncio.run(self._synthesize_neural_voice(script, temp_mp3))

            # Convert MP3 to standard WAV matching self.sample_rate
            cmd = [
                self.ffmpeg_exe,
                "-y",
                "-i", temp_mp3,
                "-ar", str(self.sample_rate),
                "-ac", "1",
                out_wav
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            return out_wav
        except Exception as e:
            # Fallback to procedural formant vocal drone if network unavailable
            print(f"[WARN] Neural TTS unavailable ({e}), using procedural vocal baritone fallback.")
            total_samples = int(self.sample_rate * duration_sec)
            t = np.linspace(0, duration_sec, total_samples, endpoint=False)
            formant = (
                0.3 * np.sin(2 * np.pi * 98.0 * t) +
                0.2 * np.sin(2 * np.pi * 196.0 * t) +
                0.15 * np.sin(2 * np.pi * 294.0 * t)
            ) * (0.8 + 0.2 * np.sin(2 * np.pi * 4.0 * t))
            self._save_wav(out_wav, formant)
            return out_wav

    # --- Timeline SFX Assembly ---

    def build_sfx_timeline_track(
        self,
        duration_sec: float,
        scene_timestamps: List[float],
        typing_intervals: List[Tuple[float, float]],
        card_reveal_times: List[float],
        filepath: Optional[str] = None
    ) -> str:
        """
        Assembles all discrete UI SFX into a single synchronized timeline WAV:
        - Typing keypresses during prompt input
        - Haptic pops on card reveals
        - Air whooshes on scene transitions
        """
        out_path = filepath or os.path.join(self.output_dir, "sfx_track.wav")
        total_samples = int(self.sample_rate * duration_sec)
        timeline = np.zeros(total_samples, dtype=np.float32)

        # Generate source samples
        click_path = self.generate_click_sfx()
        type_path = self.generate_type_sfx()
        whoosh_path = self.generate_whoosh_sfx()

        def load_wav_samples(path: str) -> np.ndarray:
            with wave.open(path, "rb") as wf:
                raw = wf.readframes(wf.getnframes())
                return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

        click_smp = load_wav_samples(click_path)
        type_smp = load_wav_samples(type_path)
        whoosh_smp = load_wav_samples(whoosh_path)

        def overlay(samples: np.ndarray, at_sec: float, gain: float = 1.0):
            start = int(at_sec * self.sample_rate)
            if start < 0 or start >= total_samples:
                return
            end = min(total_samples, start + len(samples))
            timeline[start:end] += samples[:end - start] * gain

        # 1. Overlay typing clicks during typing intervals (0.08 - 0.14s jitter)
        for t_start, t_end in typing_intervals:
            cur_t = t_start
            while cur_t < t_end:
                jitter_gain = np.random.uniform(0.75, 1.05)
                overlay(type_smp, cur_t, gain=0.85 * jitter_gain)
                cur_t += np.random.uniform(0.09, 0.14)

        # 2. Overlay haptic clicks on card reveals
        for cr in card_reveal_times:
            overlay(click_smp, cr, gain=0.95)

        # 3. Overlay subtle air whooshes slightly before scene transitions
        for st in scene_timestamps:
            if st > 0.2:
                overlay(whoosh_smp, max(0.0, st - 0.18), gain=0.65)

        # Clip and save
        timeline = np.clip(timeline, -1.0, 1.0)
        self._save_wav(out_path, timeline)
        return out_path

    # --- FFmpeg Three-Layer Audio Mixer with Sidechain Ducking ---

    def mix_audio_into_video(
        self,
        video_input: str,
        voiceover_wav: str,
        bgm_wav: str,
        sfx_wav: str,
        output_mp4: str,
        ducking_db: float = 14.0
    ) -> str:
        """
        Executes FFmpeg 3-layer audio mix with automated sidechain compression:
        [1:a] (voiceover) triggers sidechaincompress on [2:a] (BGM), reducing music by -14dB during speech.
        [3:a] (SFX) is mixed with unity punch.
        Output is encoded to AAC 192kbps and muxed with the video stream.
        """
        # Calculate compressor ratio: 8:1 with threshold 0.08 produces ~14dB gain reduction
        filter_complex = (
            "[1:a]volume=1.15,asplit=2[v_main][v_sc]; "
            "[2:a]volume=0.28[m_in]; "
            "[m_in][v_sc]sidechaincompress=threshold=0.08:ratio=8:attack=15:release=280[m_ducked]; "
            "[3:a]volume=0.75[sfx_in]; "
            "[v_main][m_ducked][sfx_in]amix=inputs=3:duration=first:dropout_transition=2[aout]"
        )

        cmd = [
            self.ffmpeg_exe,
            "-y",
            "-i", video_input,
            "-i", voiceover_wav,
            "-i", bgm_wav,
            "-i", sfx_wav,
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-movflags", "+faststart",
            output_mp4
        ]

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"FFmpeg audio mixing failed (code {proc.returncode}): {err}")

        return output_mp4

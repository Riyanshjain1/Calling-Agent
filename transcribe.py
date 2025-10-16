import subprocess
from faster_whisper import WhisperModel
from pathlib import Path
import os

# -----------------------------
# CONFIG
# -----------------------------
FFMPEG_PATH = os.path.join("bin", "ffmpeg.exe")  # your ffmpeg.exe
MODEL_NAME  = "small"        # use: tiny/base/small/medium/large-v3  (small~better than base)
FORCE_LANG  = None           # set "hi" for Hindi, "en" for English, or keep None for auto
ASSUME_OTHER_IS_LEFT = True  # if transcripts look swapped, set this to False

# VAD & decoding sensitivity (tweak if needed)
VAD_PARAMS = {"min_silence_duration_ms": 400, "speech_pad_ms": 150}
DECODE_KW  = {
    "beam_size": 5,
    "best_of": 5,
    "temperature": 0.0,
    "condition_on_previous_text": False,
    "task": "transcribe",
}

# -----------------------------
# UTIL
# -----------------------------
def _run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def _check_paths(audio_path: str):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not os.path.exists(FFMPEG_PATH):
        raise FileNotFoundError(f"FFmpeg not found at: {FFMPEG_PATH}")

def _decode_to_wav(src_path: str) -> str:
    """Decode to WAV while preserving channel count (no resample yet)."""
    out = Path(src_path).with_suffix(".raw.wav")
    _run([FFMPEG_PATH, "-y", "-i", src_path, str(out)])
    return str(out)

def _is_stereo(wav_path: str) -> bool:
    try:
        out = subprocess.check_output([FFMPEG_PATH, "-hide_banner", "-i", wav_path],
                                      stderr=subprocess.STDOUT).decode("utf-8", errors="ignore").lower()
        return ("stereo" in out) or ("2 channels" in out)
    except Exception:
        return False

def _clean_band(audio_in: str, out_path: str, mono: bool):
    """
    Clean and normalize: High-pass 100 Hz, low-pass 3800 Hz, denoise, dynamic normalize, 16 kHz.
    Telephony band ~300-3400 Hz, but we keep a bit wider.
    """
    af = "highpass=f=100,lowpass=f=3800,afftdn=nf=-25,dynaudnorm"
    args = [FFMPEG_PATH, "-y", "-i", audio_in, "-af", af]
    if mono:
        args += ["-ac", "1"]
    args += ["-ar", "16000", out_path]
    _run(args)

def _extract_channel_clean(wav_stereo: str, ch_index: int) -> str:
    """
    Extract single channel (0-left, 1-right), clean, mono 16 kHz.
    """
    mono = Path(wav_stereo).with_suffix(f".ch{ch_index+1}.raw.wav")
    # pan=mono|c0 picks left; pan=mono|c1 picks right
    pan = f"pan=mono|c0=c{ch_index}"
    _run([FFMPEG_PATH, "-y", "-i", wav_stereo, "-af", pan, str(mono)])
    out = Path(wav_stereo).with_suffix(f".ch{ch_index+1}.16k.wav")
    _clean_band(str(mono), str(out), mono=True)
    return str(out)

def _downmix_mono_16k_clean(wav_any: str) -> str:
    out = Path(wav_any).with_suffix(".mono16k.wav")
    _clean_band(wav_any, str(out), mono=True)
    return str(out)

def _whisper():
    # CPU: int8 is fastest; if you have GPU: device="cuda", compute_type="float16"
    return WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")

def _transcribe(wav_path: str) -> str:
    model = _whisper()
    segments, info = model.transcribe(
        wav_path,
        language=FORCE_LANG,
        vad_filter=True,
        vad_parameters=VAD_PARAMS,
        **DECODE_KW
    )
    return "".join(s.text for s in segments).strip()

# -----------------------------
# PUBLIC API
# -----------------------------
def transcribe_dual_or_mono(audio_path: str):
    """
    - If stereo (dual-channel), split & clean both channels, transcribe both.
      Saves:
        *_other.txt (the far-end person)
        *_agent.txt (your TTS/agent)
    - If mono, clean & transcribe once to *.txt
    """
    _check_paths(audio_path)
    print("🔊 Preparing audio...")
    wav_any = _decode_to_wav(audio_path)
    stereo = _is_stereo(wav_any)

    if stereo:
        print("🎚️ Dual-channel detected. Cleaning & splitting...")
        left16  = _extract_channel_clean(wav_any, 0)
        right16 = _extract_channel_clean(wav_any, 1)

        # Map channels → labels (flip if needed)
        if ASSUME_OTHER_IS_LEFT:
            other_wav, agent_wav = left16, right16
        else:
            other_wav, agent_wav = right16, left16

        print("🧠 Transcribing OTHER person's channel...")
        other_text = _transcribe(other_wav)

        print("🧠 Transcribing AGENT/TTS channel...")
        agent_text = _transcribe(agent_wav)

        base = Path(audio_path).with_suffix("")
        other_txt = f"{base}_other.txt"
        agent_txt = f"{base}_agent.txt"

        with open(other_txt, "w", encoding="utf-8") as f:
            f.write(other_text + "\n")
        with open(agent_txt, "w", encoding="utf-8") as f:
            f.write(agent_text + "\n")

        print(f"✅ Saved OTHER transcript: {other_txt}")
        print(f"✅ Saved AGENT transcript: {agent_txt}")

    else:
        print("🎚️ Mono detected. Cleaning & transcribing...")
        mono16 = _downmix_mono_16k_clean(wav_any)
        text = _transcribe(mono16)
        txt = Path(audio_path).with_suffix(".txt")
        with open(txt, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"✅ Transcript saved: {txt}")

# Convenience single-file transcribe (if you want to run this file directly)
if __name__ == "__main__":
    # Change this if you want to test a specific file directly
    TEST_FILE = "recording_unknown_CA278b32d3110cab926727ae98ed28175b.mp3"
    transcribe_dual_or_mono(TEST_FILE)

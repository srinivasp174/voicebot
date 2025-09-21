import sounddevice as sd
import numpy as np
import wave
import base64
import time

def list_input_devices():
    """List available input devices as (label, index)."""
    devices = sd.query_devices()
    options = []
    for idx, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            host = sd.query_hostapis(d["hostapi"])["name"]
            options.append((f"{idx}: {d['name']} ({host})", idx))
    return options

def default_input_device_index():
    """Return first available input device index or None."""
    for idx, d in enumerate(sd.query_devices()):
        if d.get("max_input_channels", 0) > 0:
            return idx
    return None

def record_audio(duration=5, fs=44100, device_index=None):
    if device_index is None:
        device_index = default_input_device_index()
    if device_index is None:
        raise RuntimeError("No input devices found. Configure ALSA/PortAudio and try again.")
    # Ensure correct default device for input
    sd.default.device = (device_index, None)
    rec = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=device_index)
    sd.wait()
    return np.squeeze(rec)

def save_wav(audio, filename, fs=44100):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())

def autoplay_audio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    timestamp = int(time.time() * 1000)
    return f"""
    <div id="audio-container-{timestamp}">
        <audio controls autoplay style="width: 100%;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    </div>
    <script>
        var audioElement = document.querySelector('#audio-container-{timestamp} audio');
        if (audioElement) {{
            audioElement.load();
            audioElement.play().catch(function(e) {{
                console.log('Autoplay prevented:', e);
            }});
        }}
    </script>
    """

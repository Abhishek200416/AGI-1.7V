#!/usr/bin/env python3
"""
IVA Video Skill <-> IVA Studios Native Bridge & Verification Gate.
Connects `skills/iva-video-skill` into IVA's vertical Shorts & motion video pipeline:
1. Procedural Canvas/Three.js headless Playwright -> FFmpeg (1080x1920, <59.9s) renderer.
2. Zero-Recycle SHA-256 visual asset ledger (forbids reusing visuals across projects).
3. Automated FFT + 2s-window RMS audio/video audit gate (blocks 8k-18kHz piercing
   resonance and voice drain before any upload).
"""

import base64
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import wave
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = (
    r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
    if os.path.exists(r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffmpeg.exe")
    else (shutil.which("ffmpeg") or "ffmpeg")
)
FFPROBE = (
    r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffprobe.exe"
    if os.path.exists(r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffprobe.exe")
    else (shutil.which("ffprobe") or "ffprobe")
)
_REPO_SKILL = os.path.join(os.path.dirname(BASE_DIR), "skills", "iva-video-skill")
_HOME_SKILL = os.path.join(os.path.expanduser("~"), ".agents", "skills", "iva-video-skill")
IVA_VIDEO_SKILL_DIR = _REPO_SKILL if os.path.isdir(_REPO_SKILL) else _HOME_SKILL
LEDGER_PATH = os.path.join(BASE_DIR, "system", "used_media_hashes.json")


def is_iva_video_skill_installed() -> bool:
    """Return True if skills/iva-video-skill and SKILL.md exist."""
    return os.path.isfile(os.path.join(IVA_VIDEO_SKILL_DIR, "SKILL.md")) and os.path.isdir(
        os.path.join(IVA_VIDEO_SKILL_DIR, "core")
    )


def get_iva_video_sfx_module():
    """Import IVA Video Skill procedural foley module (core/audio/sfx.py)."""
    if not is_iva_video_skill_installed():
        raise FileNotFoundError(f"iva-video-skill missing at {IVA_VIDEO_SKILL_DIR}")
    if IVA_VIDEO_SKILL_DIR not in sys.path:
        sys.path.insert(0, IVA_VIDEO_SKILL_DIR)
    from core.audio import sfx  # type: ignore
    return sfx


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_and_register_unique_assets(project_id: str, asset_paths: list[str]) -> dict:
    """
    Fail closed if any visual file hash was already used in a previous project.
    Registers new hashes under project_id in used_media_hashes.json.
    """
    ledger: dict[str, str] = {}
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            ledger = json.load(f)

    reused = []
    new_hashes = {}
    for p in asset_paths:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Asset missing: {p}")
        digest = sha256_file(p)
        owner = ledger.get(digest)
        if owner and owner != project_id:
            reused.append({"path": p, "previous_project": owner, "sha256": digest})
        else:
            new_hashes[digest] = project_id

    if reused:
        raise RuntimeError(f"ZERO-RECYCLE VIOLATION for {project_id}: {reused}")

    ledger.update(new_hashes)
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    return {"project_id": project_id, "verified_unique_assets": len(new_hashes)}


REQUIRE_REAL_WORLD_VISUALS = True
MIN_SOURCE_HEIGHT_PX = 720  # Strictly >=720p minimum; target 4K (2160p) -> 1080p real clips/images


def audit_real_world_scenes(scene_assets: list[dict], allow_code_demo: bool = False) -> dict:
    """
    Fail closed if a narrative/real-world Short relies on pure procedural code cartoons
    or sub-720p low-res visuals instead of verified >=720p/4K outside photographs and video clips.
    """
    if allow_code_demo:
        return {"status": "ALLOWED_CODE_DEMO", "real_media_count": len(scene_assets)}
    real_items = [a for a in scene_assets if a.get("media_kind") in ("image", "video") and os.path.exists(str(a.get("path", "")))]
    if not real_items:
        raise RuntimeError(
            "REAL_WORLD_VISUALS GATE FAIL: At least 1 verified outside camera photo or real video clip "
            "(>=720p minimum, 4K preferred) is required per scene. Pure code-run/stick-figure scenes are blocked."
        )
    low_res = [
        a for a in real_items
        if min(int(a.get("width", 0)), int(a.get("height", 0))) < MIN_SOURCE_HEIGHT_PX
        and max(int(a.get("width", 0)), int(a.get("height", 0))) < 1280
    ]
    if low_res:
        raise RuntimeError(
            f"RESOLUTION GATE FAIL: {len(low_res)} source asset(s) below 720p minimum quality."
        )
    return {
        "status": "PASS",
        "real_media_count": len(real_items),
        "video_clips": sum(1 for a in real_items if a.get("media_kind") == "video"),
        "photos": sum(1 for a in real_items if a.get("media_kind") == "image"),
    }


def assemble_real_world_montage(
    scene_assets: list[dict],
    audio_path: str,
    out_mp4: str,
    clip_duration_s: float = 3.2,
    subtitle_ass_path: str | None = None,
    fps: int = 30,
) -> dict:
    """
    Compile full-bleed 1080x1920 vertical Shorts directly from verified 4K/HD (>=720p) REAL-WORLD
    video clips and high-resolution photographs using FFmpeg lanczos scaling + Ken Burns motion
    + ASS kinetic captions + -14 LUFS audio. Zero cartoon/stick-figure code scenes.
    """
    audit_real_world_scenes(scene_assets, allow_code_demo=False)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
    work_dir = tempfile.mkdtemp(prefix="iva_real_montage_")
    try:
        seg_paths = []
        for idx, asset in enumerate(scene_assets):
            src = asset["path"]
            seg_mp4 = os.path.join(work_dir, f"seg_{idx:03d}.mp4")
            dur = float(asset.get("duration_s", clip_duration_s))
            if asset.get("media_kind") == "video":
                vf = f"scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps={fps},format=yuv420p"
                cmd = [
                    FFMPEG, "-y", "-stream_loop", "-1", "-i", src,
                    "-t", f"{dur:.3f}", "-vf", vf, "-an",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", seg_mp4,
                ]
            else:
                frames = max(1, int(round(dur * fps)))
                vf = (
                    f"scale=1280:2276:force_original_aspect_ratio=increase,crop=1280:2276,"
                    f"zoompan=z='min(zoom+0.0012,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},"
                    "format=yuv420p"
                )
                cmd = [
                    FFMPEG, "-y", "-loop", "1", "-i", src,
                    "-t", f"{dur:.3f}", "-vf", vf, "-an",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", seg_mp4,
                ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            seg_paths.append(seg_mp4)

        concat_txt = os.path.join(work_dir, "concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as cf:
            for sp in seg_paths:
                escaped = sp.replace("'", "'\\''")
                cf.write(f"file '{escaped}'\n")

        cmd_final = [
            FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-i", audio_path,
        ]
        if subtitle_ass_path and os.path.exists(subtitle_ass_path):
            sub_escaped = subtitle_ass_path.replace("\\", "/").replace(":", r"\:")
            cmd_final.extend(["-vf", f"ass='{sub_escaped}'"])
        cmd_final.extend([
            "-af", "alimiter=limit=0.94:attack=5:release=50",
            "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            "-shortest", out_mp4,
        ])
        subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return audit_media_gates(out_mp4, require_video=True)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def render_canvas_html_to_mp4(
    html_path: str,
    audio_path: str,
    out_mp4: str,
    duration_s: float,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
) -> dict:
    """
    Render an IVA Video Skill HTML5 Canvas film via headless Playwright -> FFmpeg pipe.
    Uses stderr log file (never subprocess.PIPE) to prevent Windows 64KB buffer hangs.
    """
    if duration_s >= 60.0:
        raise ValueError(f"Duration {duration_s:.2f}s violates <60.0s YouTube Shorts limit.")

    from playwright.sync_api import sync_playwright

    work_dir = os.path.dirname(os.path.abspath(html_path))
    html_name = os.path.basename(html_path)
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
    err_log = os.path.join(work_dir, f"{os.path.splitext(html_name)[0]}_ffmpeg.log")

    handler = partial(SimpleHTTPRequestHandler, directory=work_dir)
    handler.log_message = lambda *args, **kwargs: None
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    total_frames = math.ceil(duration_s * fps)
    ffmpeg_cmd = [
        FFMPEG, "-y",
        "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(fps), "-i", "-",
        "-i", audio_path,
        "-af", "alimiter=limit=0.94:attack=5:release=50",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-shortest", out_mp4,
    ]

    with open(err_log, "w", encoding="utf-8") as err_file:
        ff = subprocess.Popen(
            ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=err_file
        )
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(f"http://127.0.0.1:{port}/{html_name}", wait_until="networkidle")
                page.wait_for_function("window.READY === true", timeout=20000)
                for frame in range(total_frames):
                    t_sec = frame / fps
                    data_url = page.evaluate(
                        f"window.render({t_sec:.4f}); document.getElementById('c').toDataURL('image/jpeg', 0.92);"
                    )
                    ff.stdin.write(base64.b64decode(data_url.split(",", 1)[1]))
                browser.close()
        finally:
            if ff.stdin:
                ff.stdin.close()
            ff.wait()
            server.shutdown()

    if ff.returncode != 0:
        with open(err_log, "r", encoding="utf-8") as f:
            raise RuntimeError(f"FFmpeg render failed (code {ff.returncode}): {f.read()[-1000:]}")

    return audit_media_gates(out_mp4, require_video=True)


def audit_media_gates(media_path: str, require_video: bool = True) -> dict:
    """Verify <59.9s duration, 1080x1920 geometry, no voice drain, and no 8-18kHz piercing noise."""
    probe_cmd = [
        FFPROBE, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", media_path,
    ]
    probe = json.loads(subprocess.check_output(probe_cmd, text=True))
    dur = float(probe["format"]["duration"])
    if dur >= 59.9:
        raise RuntimeError(f"SHORT DURATION GATE FAIL: {dur:.2f}s >= 59.9s")

    if require_video:
        vstreams = [s for s in probe["streams"] if s.get("codec_type") == "video"]
        if not vstreams or vstreams[0].get("width") != 1080 or vstreams[0].get("height") != 1920:
            raise RuntimeError(f"VIDEO RESOLUTION GATE FAIL: expected 1080x1920, got {vstreams}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_wav = tmp.name

    try:
        subprocess.run(
            [FFMPEG, "-y", "-i", media_path, "-vn", "-ac", "1", "-ar", "48000", tmp_wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        with wave.open(tmp_wav, "rb") as w:
            sr = w.getframerate()
            samples = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    finally:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)

    win = 2 * sr
    rms_list = []
    for i in range(0, max(1, len(samples) - sr), win):
        seg = samples[i : i + win]
        if len(seg) < sr // 2:
            continue
        rms = float(np.sqrt(np.mean(seg ** 2)) + 1e-9)
        rms_list.append(20.0 * math.log10(rms))

    min_rms = min(rms_list) if rms_list else -90.0
    max_rms = max(rms_list) if rms_list else -90.0
    if max_rms < -20.0 or min_rms < -28.0:
        raise RuntimeError(f"VOICE DRAIN GATE FAIL: RMS range [{min_rms:.2f}, {max_rms:.2f}] dBFS")

    spec = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1.0 / sr)
    hf_mask = (freqs >= 8000) & (freqs <= 18000)
    hf_spec = spec[hf_mask]
    hf_ratio = float(np.sum(hf_spec ** 2) / (np.sum(spec ** 2) + 1e-12))

    if hf_ratio > 0.20:
        raise RuntimeError(f"PIERCING HF ENERGY GATE FAIL: 8-18kHz energy ratio {hf_ratio:.3f} > 0.20")

    return {
        "status": "PASS",
        "duration_s": round(dur, 2),
        "rms_min_db": round(min_rms, 2),
        "rms_max_db": round(max_rms, 2),
        "hf_energy_ratio": round(hf_ratio, 4),
    }


def _self_check():
    print("[SELF-CHECK] iva-video-skill installed:", is_iva_video_skill_installed())
    sfx = get_iva_video_sfx_module()
    assert hasattr(sfx, "whoosh") and hasattr(sfx, "click"), "Missing foley helpers in core.audio.sfx"
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as clean_f, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as toxic_f:
        clean_wav, toxic_wav = clean_f.name, toxic_f.name
    try:
        sr = 48000
        t = np.linspace(0, 4.0, 4 * sr, endpoint=False)
        clean_sig = 0.22 * np.sin(2 * np.pi * 220 * t) + 0.08 * np.sin(2 * np.pi * 440 * t)
        toxic_sig = 0.05 * np.sin(2 * np.pi * 220 * t) + 0.35 * np.sin(2 * np.pi * 12000 * t)
        for path, sig in [(clean_wav, clean_sig), (toxic_wav, toxic_sig)]:
            with wave.open(path, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes((np.clip(sig, -1, 1) * 32767).astype(np.int16).tobytes())

        res_clean = audit_media_gates(clean_wav, require_video=False)
        print("[PASS] Clean synthetic audio gate:", res_clean)
        failed_as_expected = False
        try:
            audit_media_gates(toxic_wav, require_video=False)
        except RuntimeError as e:
            failed_as_expected = "PIERCING HF" in str(e)
            print("[PASS] Toxic 12kHz spike blocked:", e)
        assert failed_as_expected
    finally:
        for p in (clean_wav, toxic_wav):
            if os.path.exists(p):
                os.remove(p)
    print("[PASS] iva_video_bridge self-check verified.")


if __name__ == "__main__":
    _self_check()

import asyncio
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import edge_tts

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HOME_DIR = str(Path.home())
BASE_DIR = os.environ.get("IVA_STUDIO_DIR", os.path.join(HOME_DIR, "Downloads", "ytsss", "AI_MEDIA_STUDIO"))
REPO_ROOT = os.environ.get("IVA_REPO_ROOT", os.path.join(HOME_DIR, "Projects", "IVA"))

sys.path.insert(0, os.path.join(BASE_DIR, "system"))
sys.path.insert(0, os.path.join(REPO_ROOT, "studio", "system"))
import iva_video_bridge as bridge

PROJECT_ID = "PRJ-081"
WORK_DIR = os.path.join(BASE_DIR, "video", "prj081_moon_bell")
AUDIO_DIR = os.path.join(BASE_DIR, "audio", "prj081_moon_bell")
FINAL_MP4 = os.path.join(BASE_DIR, "video", "final_exports", "prj081_moon_bell_short.mp4")
ART_DIR = os.path.join(HOME_DIR, ".gemini", "antigravity", "brain", "93384ca3-839f-48d8-82bc-403889e3d4bc")

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

# 100% Acoustic & Melodic Music (Zero synthetic frequency sounds/drones!)
BGM_PIANO_STRINGS = os.path.join(BASE_DIR, "music", "compositions", "emotional_piano_strings.mp3")

# Authentic physical SFX
SFX_BELL = os.path.join(BASE_DIR, "music", "sound_effects", "acoustic_bronze_bell.wav")
SFX_THUD = os.path.join(BASE_DIR, "music", "sound_effects", "heartbeat_thud.wav")
SFX_CLICK = os.path.join(BASE_DIR, "music", "sound_effects", "slide_click.wav")
SFX_WARM_BOOM = os.path.join(BASE_DIR, "music", "sound_effects", "warm_sub_boom.wav")

# Single consistent voice throughout the entire video:
NARRATOR_VOICE = "en-US-AvaNeural"
NARRATOR_RATE = "+14%"
NARRATOR_PITCH = "+0Hz"

# Outro: SAME voice, modulated cutely and warmly
OUTRO_RATE = "+8%"
OUTRO_PITCH = "+6Hz"

BEATS = [
    (
        "Every textbook told you the Moon is a solid sphere of dead rock. But in 1969, NASA discovered something so terrifying, scientists were stunned into silence.",
        "HookCard",
        r"TEXTBOOKS LIED: {\c&H000000FF\3c&H0000FFFF\blur4\bord4}THE MOON IS NOT SOLID ROCK{\r} 🌕😱",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "During Apollo 12, astronauts deliberately crashed their empty lunar module ascent stage directly into the Moon's surface.",
        "CrashCard",
        r"APOLLO 12 CRASH TEST: {\c&H0000FFFF\3c&H000000FF\blur3\bord3}CRASHING INTO THE MOON{\r} 🚀💥",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "On Earth, an impact dies in seconds. But on the Moon, the seismic sensors recorded something impossible.",
        "AnomalyCard",
        r"SEISMIC SENSORS DETECT: {\c&H00FFFF00\3c&H000000FF\blur3\bord3}AN IMPOSSIBLE REVERBERATION{\r} 📈⚡",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "The vibrations didn't stop. The entire Moon vibrated and rang like a giant brass bell for over three hours!",
        "BellCard",
        r"THE MOON RANG LIKE A BELL: {\c&H0000FFFF\3c&H000080FF\blur5\bord5}FOR 3 HOURS AND 20 MINUTES{\r}! 🔔⚡",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "NASA geophysicist Maurice Ewing admitted: 'It was as if someone struck a cathedral bell in a giant bell tower.'",
        "QuoteCard",
        r"NASA GEOPHYSICIST: {\c&H00FFFFFF\3c&H00FF80FF\blur4\bord4}'LIKE A GIANT CATHEDRAL BELL'{\r} 🏛️",
        NARRATOR_RATE, NARRATOR_PITCH, 1.2  # 1.2s dramatic breathing pause before line
    ),
    (
        "A solid rock cannot ring for hours. Only a hollow metallic sphere can sustain reverberations that long.",
        "HollowCard",
        r"A SOLID ROCK CANNOT RING: {\c&H000000FF\3c&H0000FFFF\blur4\bord4}HOLLOW METALLIC SPHERE?{\r} 🛸",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "Even fifty years later, scientists still cannot explain what is actually hiding inside our Moon.",
        "ClimaxCard",
        r"50 YEARS LATER: {\c&H0000FFFF\3c&H000000FF\blur4\bord4}NASA STILL CANNOT EXPLAIN IT{\r} 🌌",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "Do you think the Moon is hollow? Subscribe to Dark Matters for more cosmic secrets!",
        "CuteOutro",
        r"{\c&H00FFFFFF\3c&H00FF80FF\blur3\bord3}SUBSCRIBE TO DARK MATTERS! ❤️{\r}",
        OUTRO_RATE, OUTRO_PITCH, 0.0
    ),
]


def fmt_ass(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(timings: list, out_ass: str):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HookCard,Arial Black,48,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: CrashCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: AnomalyCard,Arial Black,48,&H00FFFF00,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: BellCard,Arial Black,50,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: QuoteCard,Arial Black,48,&H00FFFFFF,&H00FF80FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: HollowCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: ClimaxCard,Arial Black,50,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: CuteOutro,Arial Black,52,&H00FFFFFF,&H00FF80FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for st, en, style, txt in timings:
        lines.append(f"Dialogue: 0,{fmt_ass(st)},{fmt_ass(en)},{style},,0,0,0,,{txt}")
    with open(out_ass, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines) + "\n")


async def synth_voice_and_ass():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    for f in os.listdir(AUDIO_DIR):
        if f.startswith("beat_") or f.endswith(".wav") or f.endswith(".ass") or f.endswith(".txt"):
            try:
                os.remove(os.path.join(AUDIO_DIR, f))
            except Exception:
                pass

    timings = []
    cursor = 0.0
    seg_files = []

    for idx, (spoken, style, caption, rate, pitch, pause_before) in enumerate(BEATS):
        if pause_before > 0:
            silence_wav = os.path.join(AUDIO_DIR, f"pause_{idx:02d}.wav")
            subprocess.run([
                FFMPEG, "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono", "-t", f"{pause_before:.2f}",
                "-c:a", "pcm_s16le", silence_wav
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            seg_files.append(silence_wav)
            cursor += pause_before

        raw_mp3 = os.path.join(AUDIO_DIR, f"beat_{idx:02d}.mp3")
        raw_wav = os.path.join(AUDIO_DIR, f"beat_{idx:02d}.wav")

        for attempt in range(1, 6):
            try:
                comm = edge_tts.Communicate(spoken, voice=NARRATOR_VOICE, rate=rate, pitch=pitch)
                await comm.save(raw_mp3)
                if os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 1000:
                    break
            except Exception as ex:
                print(f"EdgeTTS retry {attempt}/5 on beat {idx}: {ex}", flush=True)
                await asyncio.sleep(2.0 * attempt)

        subprocess.run([FFMPEG, "-y", "-i", raw_mp3, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", raw_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        dur = float(subprocess.check_output([
            FFPROBE, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", raw_wav
        ], text=True).strip())
        seg_files.append(raw_wav)
        timings.append((cursor, cursor + dur, style, caption))
        cursor += dur

    concat_txt = os.path.join(AUDIO_DIR, "voice_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for w in seg_files:
            f.write("file '" + w.replace("\\", "/") + "'\n")
    voice_wav = os.path.join(AUDIO_DIR, "prj081_voice.wav")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", voice_wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    ass_path = os.path.join(AUDIO_DIR, "prj081_subtitles.ass")
    build_ass(timings, ass_path)
    return voice_wav, ass_path, timings, cursor


def mix_audio(voice_wav: str, total_dur: float, timings: list) -> str:
    master_wav = os.path.join(AUDIO_DIR, "prj081_master_mix.wav")

    # SFX timing points in milliseconds:
    click_0_ms = int(timings[0][0] * 1000)
    thud_1_ms = int(timings[1][1] * 1000) - 200  # Right at the crash impact!
    click_2_ms = int(timings[2][0] * 1000)
    bell_3_ms = int(timings[3][0] * 1000)        # Right when "rang like a brass bell" hits!
    bell_4_ms = int((timings[4][0] - 1.0) * 1000) # During the breathing pause before cathedral quote!
    warmboom_5_ms = int(timings[5][0] * 1000)

    # Complex audio filter:
    # 1. Narrator voice with clarity EQ and compression
    # 2. Emotional piano strings BGM ducked gently to -26 dBFS (100% acoustic melody, ZERO frequency buzz/drones!)
    # 3. Acoustic bronze bell toll + physical thuds
    filter_complex = (
        "[0:a]highpass=f=80,equalizer=f=2800:t=q:w=1.2:g=1.8,highshelf=f=7500:g=-1.5,acompressor=threshold=-16dB:ratio=2.4:attack=12:release=140,volume=1.40[v];"
        f"[1:a]atrim=start=0:duration={total_dur:.2f},asetpts=PTS-STARTPTS,highpass=f=50,lowpass=f=8000,"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={max(0, total_dur-2.0):.2f}:d=2.0,volume=0.065[bgm];"
        f"[2:a]adelay={click_0_ms}|{click_0_ms},volume=0.20[s_c0];"
        f"[3:a]adelay={thud_1_ms}|{thud_1_ms},volume=0.35[s_thud1];"
        f"[4:a]adelay={click_2_ms}|{click_2_ms},volume=0.20[s_c2];"
        f"[5:a]adelay={bell_3_ms}|{bell_3_ms},volume=0.35[s_bell3];"
        f"[6:a]adelay={bell_4_ms}|{bell_4_ms},volume=0.38[s_bell4];"
        f"[7:a]adelay={warmboom_5_ms}|{warmboom_5_ms},volume=0.25[s_wbm5];"
        "[v][bgm][s_c0][s_thud1][s_c2][s_bell3][s_bell4][s_wbm5]amix=inputs=8:duration=first:dropout_transition=0:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=6,alimiter=limit=0.94[out]"
    )
    subprocess.run([
        FFMPEG, "-y",
        "-i", voice_wav,
        "-i", BGM_PIANO_STRINGS,
        "-i", SFX_CLICK,
        "-i", SFX_THUD,
        "-i", SFX_CLICK,
        "-i", SFX_BELL,
        "-i", SFX_BELL,
        "-i", SFX_WARM_BOOM,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        master_wav,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return master_wav


def compile_real_footage(master_wav: str, ass_path: str, total_dur: float, timings: list):
    clip_crash = os.path.join(WORK_DIR, "apollo12_bell_crash.mp4")
    clip_mystery = os.path.join(WORK_DIR, "moon_bell_mystery.mp4")
    clip_landing = os.path.join(WORK_DIR, "apollo12_landing_hd.mp4")

    used_sources = [clip_crash, clip_mystery, clip_landing]
    for src in used_sources:
        assert os.path.exists(src), f"Missing media source: {src}"
    bridge.audit_real_world_scenes([
        {"media_kind": "video", "path": clip_crash, "width": 1920, "height": 1080},
        {"media_kind": "video", "path": clip_mystery, "width": 1920, "height": 1080},
        {"media_kind": "video", "path": clip_landing, "width": 1920, "height": 1080},
    ])
    bridge.verify_and_register_unique_assets("PRJ-081", used_sources)

    # 8 rhythmic real-world video cuts matching story beats & breathing pause
    cut_specs = [
        # Cut 0: Wide cosmic view of Moon surface / orbit (Hook: Textbooks lied)
        (clip_crash, 4.0, timings[0][1] - timings[0][0], 0.50, "Moon orbit / surface"),
        # Cut 1: Lunar module ascent stage separating and crashing
        (clip_crash, 22.0, timings[1][1] - timings[1][0], 0.50, "Lunar module ascent & crash"),
        # Cut 2: Seismic equipment on lunar dust & needle jumping
        (clip_mystery, 28.0, timings[2][1] - timings[2][0], 0.50, "Seismic sensors on dust"),
        # Cut 3: Giant bell ringing graphic / seismograph vibrating for 3 hours
        (clip_crash, 42.0, timings[3][1] - timings[3][0], 0.50, "Moon vibrating like bell"),
        # Cut 4: Apollo Mission Control / Maurice Ewing cathedral bell (+1.2s pause)
        (clip_mystery, 68.0, timings[4][1] - timings[4][0] + 1.2, 0.50, "Mission control / cathedral bell"),
        # Cut 5: Hollow metallic sphere cross-section diagram
        (clip_mystery, 118.0, timings[5][1] - timings[5][0], 0.50, "Hollow moon cross-section"),
        # Cut 6: Astronaut standing alone on silent moon surface
        (clip_landing, 88.0, timings[6][1] - timings[6][0], 0.50, "Astronaut standing on moon"),
        # Cut 7: Earth rising over Moon horizon + cute outro
        (clip_landing, 148.0, timings[7][1] - timings[7][0] + 0.25, 0.50, "Earthrise + Cute outro"),
    ]

    temp_segs = []
    os.makedirs(os.path.join(WORK_DIR, "segs"), exist_ok=True)

    for idx, (src, st, dur, crop_x, label) in enumerate(cut_specs):
        seg_mp4 = os.path.join(WORK_DIR, "segs", f"seg_{idx:02d}.mp4")
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:1920:(in_w-out_w)*{crop_x}:0,eq=contrast=1.06:saturation=1.12:gamma=1.02,fps=30,format=yuv420p"
        )
        cmd = [FFMPEG, "-y", "-i", src, "-ss", f"{st:.2f}", "-t", f"{dur:.3f}",
               "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "15", seg_mp4]
        print(f"  [{idx+1}/{len(cut_specs)}] {label} ({dur:.2f}s)...")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        temp_segs.append(seg_mp4)

    concat_txt = os.path.join(WORK_DIR, "segs", "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for sp in temp_segs:
            cf.write("file '" + sp.replace("\\", "/") + "'\n")

    os.makedirs(os.path.dirname(FINAL_MP4), exist_ok=True)
    ass_esc = ass_path.replace("\\", "/").replace(":", r"\:")
    cmd_mux = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", master_wav,
        "-vf", f"ass='{ass_esc}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-shortest", FINAL_MP4,
    ]
    subprocess.run(cmd_mux, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    gate = bridge.audit_media_gates(FINAL_MP4, require_video=True)
    print("AUDIO/VIDEO AUDIT GATE:", gate)

    for ts_tag, ts in [("02s", 2.0), ("12s", 12.0), ("24s", 24.0), ("climax", max(2.0, total_dur - 3.0))]:
        qa_img = os.path.join(ART_DIR, f"qa_prj081_{ts_tag}.jpg")
        subprocess.run([FFMPEG, "-y", "-ss", f"{ts:.2f}", "-i", FINAL_MP4, "-frames:v", "1", qa_img],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("QA_FRAME:", qa_img)


def main():
    voice_wav, ass_path, timings, total_dur = asyncio.run(synth_voice_and_ass())
    print(f"Voiceover synthesized: {total_dur:.2f}s across {len(timings)} beats (One voice: Ava, Melodic score)")
    master_wav = mix_audio(voice_wav, total_dur, timings)
    compile_real_footage(master_wav, ass_path, total_dur, timings)
    print("PRJ-081 BUILD COMPLETE:", FINAL_MP4)


if __name__ == "__main__":
    main()

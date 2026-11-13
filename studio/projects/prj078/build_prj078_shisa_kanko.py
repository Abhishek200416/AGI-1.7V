import asyncio
import datetime
import json
import os
from pathlib import Path
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

WORK_DIR = os.path.join(BASE_DIR, "video", "prj078_shisa_kanko")
AUDIO_DIR = os.path.join(BASE_DIR, "audio", "prj078_shisa_kanko")
FINAL_MP4 = os.path.join(BASE_DIR, "video", "final_exports", "prj078_shisa_kanko_short.mp4")
ART_DIR = os.path.join(HOME_DIR, ".gemini", "antigravity", "brain", "93384ca3-839f-48d8-82bc-403889e3d4bc")

FFMPEG = r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffprobe.exe"

# Tension & investigative electronic pulse track
BGM_TRACK = os.path.join(BASE_DIR, "music", "compositions", "investigative_electronic_pulse.mp3")
SFX_CLICK = os.path.join(BASE_DIR, "music", "sound_effects", "slide_click.wav")
SFX_WHOOSH = os.path.join(BASE_DIR, "music", "sound_effects", "whoosh_transition.wav")
SFX_BOOM = os.path.join(BASE_DIR, "music", "sound_effects", "warm_sub_boom.wav")

# Voice casting according to operator directives:
# Male voice for suspicious hook, relatable setup, and hard statistics
MALE_VOICE = "en-US-ChristopherNeural"
MALE_RATE = "+12%"
MALE_PITCH = "+0Hz"

# Female voice for cultural context, neuroscience explanation, and home life tip
FEMALE_VOICE = "en-US-AvaNeural"
FEMALE_RATE = "+14%"
FEMALE_PITCH = "+0Hz"

# Cute female outro voice for CTA
OUTRO_VOICE = "en-US-AnaNeural"
OUTRO_RATE = "+6%"
OUTRO_PITCH = "+8Hz"

BEATS = [
    (
        "If you visit Japan, train drivers point aggressively at empty air and shout to themselves. To tourists, it looks completely crazy.",
        "HookCard",
        r"WHY JAPANESE TRAIN DRIVERS {\c&H0000FFFF}POINT AT EMPTY AIR...{\r} 🚅",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "They point at speedometers, empty tracks, and doors, yelling out loud with every single step.",
        "HookCard",
        r"POINTING AT SPEEDOMETERS: {\c&H00FF80FF}YELLING OUT LOUD{\r}!",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "This isn't superstition. It's a genius 100-year-old safety system called Shisa Kanko: Pointing and Calling.",
        "ExplainCard",
        r"IT'S A 100-YEAR SYSTEM: {\c&H0000FFFF}SHISA KANKO (POINT & CALL){\r}",
        FEMALE_VOICE, FEMALE_RATE, FEMALE_PITCH
    ),
    (
        "Routine tasks put your brain on dangerous autopilot. But pointing fires your motor cortex, looking activates your eyes, and calling activates your ears.",
        "ScienceCard",
        r"BRAIN AUTOPILOT BROKEN: {\c&H00FFFF00}EYES, HAND & VOICE SYNC{\r} 🧠",
        FEMALE_VOICE, FEMALE_RATE, FEMALE_PITCH
    ),
    (
        "Studies found doing tasks silently causes 2.4 errors per thousand. But with Pointing and Calling, mistakes drop by a massive 85 percent!",
        "StatCard",
        r"ACCIDENTS PLUMMET: {\c&H0000FFFF}85% REDUCTION IN HUMAN ERROR{\r} 📉",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "Japan's bullet trains have carried over 10 billion passengers with zero fatal collisions or derailments.",
        "ClimaxCard",
        r"10 BILLION PASSENGERS: {\c&H00FF80FF}ZERO FATAL CRASHES IN 60 YRS{\r} ⚡",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "Next time you leave home, point at your locked door and say 'Door is locked!' You will never worry about your keys again.",
        "TipCard",
        r"TRY IT AT HOME: {\c&H0000FFFF}'DOOR IS LOCKED!' NEVER FORGET{\r} 🔑",
        FEMALE_VOICE, FEMALE_RATE, FEMALE_PITCH
    ),
    (
        "Please subscribe to our channel!",
        "CuteOutro",
        r"{\c&H00FF80FF}PLEASE SUBSCRIBE TO OUR CHANNEL! ❤️{\r}",
        OUTRO_VOICE, OUTRO_RATE, OUTRO_PITCH
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
Style: ExplainCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: ScienceCard,Arial Black,48,&H00FFFF00,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: StatCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: ClimaxCard,Arial Black,50,&H00FFFFFF,&H00FF80FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: TipCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
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
    # Clear old cache to force fresh audio with updated timings
    for f in os.listdir(AUDIO_DIR):
        if f.startswith("beat_") or f.endswith(".wav") or f.endswith(".ass") or f.endswith(".txt"):
            try:
                os.remove(os.path.join(AUDIO_DIR, f))
            except Exception:
                pass
    seg_wavs = []
    timings = []
    cursor = 0.0
    for idx, (spoken, style, caption, voice, rate, pitch) in enumerate(BEATS):
        raw_mp3 = os.path.join(AUDIO_DIR, f"beat_{idx:02d}.mp3")
        raw_wav = os.path.join(AUDIO_DIR, f"beat_{idx:02d}.wav")

        for attempt in range(1, 6):
            try:
                comm = edge_tts.Communicate(spoken, voice=voice, rate=rate, pitch=pitch)
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
        seg_wavs.append(raw_wav)
        timings.append((cursor, cursor + dur, style, caption))
        cursor += dur

    concat_txt = os.path.join(AUDIO_DIR, "voice_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for w in seg_wavs:
            f.write("file '" + w.replace("\\", "/") + "'\n")
    voice_wav = os.path.join(AUDIO_DIR, "prj078_voice.wav")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", voice_wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    ass_path = os.path.join(AUDIO_DIR, "prj078_subtitles.ass")
    build_ass(timings, ass_path)
    return voice_wav, ass_path, timings, cursor


def mix_audio(voice_wav: str, total_dur: float, timings: list) -> str:
    master_wav = os.path.join(AUDIO_DIR, "prj078_master_mix.wav")

    # SFX timing points in milliseconds:
    click_0_ms = int(timings[0][0] * 1000)
    whoosh_1_ms = int(timings[1][0] * 1000)
    click_2_ms = int(timings[2][0] * 1000)
    click_3_ms = int(timings[3][0] * 1000)
    boom_4_ms = int(timings[4][0] * 1000)
    whoosh_5_ms = int(timings[5][0] * 1000)
    click_6_ms = int(timings[6][0] * 1000)

    # Master audio processing:
    # 1. Voice: Multi-voice (Christopher + Ava + Ana), clarity EQ, compressor
    # 2. BGM: Investigative electronic pulse ducked to -28 dBFS
    # 3. SFX: Subtle clicks, whooshes, and warm sub booms on key points
    filter_complex = (
        "[0:a]highpass=f=80,equalizer=f=2800:t=q:w=1.2:g=1.8,highshelf=f=7500:g=-1.5,acompressor=threshold=-16dB:ratio=2.4:attack=12:release=140,volume=1.40[v];"
        f"[1:a]atrim=start=0:duration={total_dur:.2f},asetpts=PTS-STARTPTS,highpass=f=50,equalizer=f=2800:t=q:w=1.2:g=-4.0,highshelf=f=4200:g=-6.5,lowpass=f=8000,"
        f"afade=t=in:st=0:d=1.0,afade=t=out:st={max(0, total_dur-1.5):.2f}:d=1.5,volume=0.048[bgm];"
        f"[2:a]adelay={click_0_ms}|{click_0_ms},volume=0.22[c0];"
        f"[3:a]adelay={whoosh_1_ms}|{whoosh_1_ms},volume=0.18[w1];"
        f"[4:a]adelay={click_2_ms}|{click_2_ms},volume=0.20[c2];"
        f"[5:a]adelay={click_3_ms}|{click_3_ms},volume=0.22[c3];"
        f"[6:a]adelay={boom_4_ms}|{boom_4_ms},volume=0.26[bm4];"
        f"[7:a]adelay={whoosh_5_ms}|{whoosh_5_ms},volume=0.18[w5];"
        f"[8:a]adelay={click_6_ms}|{click_6_ms},volume=0.20[c6];"
        "[v][bgm][c0][w1][c2][c3][bm4][w5][c6]amix=inputs=9:duration=first:dropout_transition=0:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=6,alimiter=limit=0.94[out]"
    )
    subprocess.run([
        FFMPEG, "-y",
        "-i", voice_wav,
        "-i", BGM_TRACK,
        "-i", SFX_CLICK,
        "-i", SFX_WHOOSH,
        "-i", SFX_CLICK,
        "-i", SFX_CLICK,
        "-i", SFX_BOOM,
        "-i", SFX_WHOOSH,
        "-i", SFX_CLICK,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        master_wav,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return master_wav


def compile_real_footage(master_wav: str, ass_path: str, total_dur: float, timings: list):
    clip_atlas = os.path.join(WORK_DIR, "shisa_kanko_atlas.mp4")
    clip_railway = os.path.join(WORK_DIR, "shisa_kanko_railway.mp4")

    used_sources = [clip_atlas, clip_railway]
    for src in used_sources:
        assert os.path.exists(src), f"Missing real media source: {src}"
    bridge.audit_real_world_scenes([
        {"media_kind": "video", "path": clip_atlas, "width": 1920, "height": 1080},
        {"media_kind": "video", "path": clip_railway, "width": 1920, "height": 1080},
    ])
    bridge.verify_and_register_unique_assets("PRJ-078", used_sources)

    # 8 rhythmic real-world video cuts matching exactly with the story beats
    cut_specs = [
        # Cut 0: Conductor standing tall, pointing forward with white glove and red flag (Male hook)
        ("video", clip_atlas, 13.0, timings[0][1] - timings[0][0], "(in_w-out_w)*0.55", "Conductor pointing along platform with glove and flag"),
        # Cut 1: Conductor on platform pointing at station sign and train (Male hook)
        ("video", clip_atlas, 47.5, timings[1][1] - timings[1][0], "(in_w-out_w)*0.35", "Conductor pointing up at sign and calling"),
        # Cut 2: Illustrated Shisa Kanko safety handbook poster (Female explanation)
        ("video", clip_atlas, 93.5, timings[2][1] - timings[2][0], "(in_w-out_w)*0.38", "Illustrated handbook showing pointing and calling rules"),
        # Cut 3: Train driver in cabin pointing at gauge and calling out (Female neuroscience)
        ("video", clip_railway, 47.5, timings[3][1] - timings[3][0], "(in_w-out_w)*0.45", "Driver in cabin pointing at gauge and calling out"),
        # Cut 4: Driver pointing directly at speedometer on moving train (Male statistics)
        ("video", clip_railway, 134.5, timings[4][1] - timings[4][0], "(in_w-out_w)*0.55", "Driver pointing directly at speedometer on moving train"),
        # Cut 5: Shinkansen bullet train at station with conductor (Male bullet train record)
        ("video", clip_railway, 178.5, timings[5][1] - timings[5][0], "(in_w-out_w)*0.48", "Shinkansen bullet train at station with conductor"),
        # Cut 6: Driver in morning sun pointing at schedule (Female home tip)
        ("video", clip_railway, 116.5, timings[6][1] - timings[6][0], "(in_w-out_w)*0.45", "Driver in morning sun pointing at schedule"),
        # Cut 7: Station attendant pointing along bullet train track + Cute outro (Cute outro)
        ("video", clip_railway, 209.0, timings[7][1] - timings[7][0] + 0.25, "(in_w-out_w)*0.52", "Station attendant pointing along bullet train track + Cute outro"),
    ]

    temp_segs = []
    os.makedirs(os.path.join(WORK_DIR, "segs"), exist_ok=True)

    for idx, (kind, src, st, dur, crop_x, label) in enumerate(cut_specs):
        seg_mp4 = os.path.join(WORK_DIR, "segs", f"seg_{idx:02d}.mp4")
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:1920:{crop_x}:0,eq=contrast=1.06:saturation=1.14:gamma=1.02,fps=30,format=yuv420p"
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
        qa_img = os.path.join(ART_DIR, f"qa_prj078_{ts_tag}.jpg")
        subprocess.run([FFMPEG, "-y", "-ss", f"{ts:.2f}", "-i", FINAL_MP4, "-frames:v", "1", qa_img],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("QA_FRAME:", qa_img)


def main():
    voice_wav, ass_path, timings, total_dur = asyncio.run(synth_voice_and_ass())
    print(f"Voiceover synthesized: {total_dur:.2f}s across {len(timings)} beats (Christopher + Ava + Ana)")
    master_wav = mix_audio(voice_wav, total_dur, timings)
    compile_real_footage(master_wav, ass_path, total_dur, timings)
    print("PRJ-078 BUILD COMPLETE:", FINAL_MP4)


if __name__ == "__main__":
    main()

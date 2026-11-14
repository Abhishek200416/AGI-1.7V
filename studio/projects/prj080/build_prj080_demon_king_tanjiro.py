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

PROJECT_ID = "PRJ-080"
WORK_DIR = os.path.join(BASE_DIR, "video", "prj080_demon_king_tanjiro")
AUDIO_DIR = os.path.join(BASE_DIR, "audio", "prj080_demon_king_tanjiro")
FINAL_MP4 = os.path.join(BASE_DIR, "video", "final_exports", "prj080_demon_king_tanjiro_short.mp4")
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

# Atmospheric scores & SFX
BGM_DRONE = os.path.join(BASE_DIR, "music", "compositions", "cinematic_tension_drone.mp3")
BGM_PIANO = os.path.join(BASE_DIR, "music", "compositions", "tragic_sad_piano.mp3")

SFX_HEARTBEAT = os.path.join(BASE_DIR, "music", "sound_effects", "heartbeat_thud.wav")
SFX_BOOM = os.path.join(BASE_DIR, "music", "sound_effects", "dramatic_boom.wav")
SFX_RISER = os.path.join(BASE_DIR, "music", "sound_effects", "suspense_riser.wav")
SFX_WHOOSH = os.path.join(BASE_DIR, "music", "sound_effects", "whoosh_transition.wav")
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
        "You thought Muzan was Demon Slayer's greatest monster. But the author hid a darker secret: Tanjiro was the real Demon King.",
        "HookCard",
        r"THE DARKEST TRUTH IN DEMON SLAYER: {\c&H000000FF\3c&H0000FFFF\blur4\bord4}TANJIRO WAS THE DEMON KING{\r} 👺🩸",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "As Muzan dissolved into the morning sun, his dying heart made one last terrifying choice.",
        "ExplainCard",
        r"MUZAN DISSOLVING IN THE SUN: {\c&H0000FFFF\3c&H000000FF\blur3\bord3}ONE LAST TERRIFYING CHOICE{\r} ⚡",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "Tanjiro had died in battle. But before his soul passed, Muzan injected all his demonic blood directly into Tanjiro's heart.",
        "MysteryCard",
        r"MUZAN'S BLOOD POURED IN: {\c&H000000FF\3c&H000080FF\blur4\bord4}DIRECTLY INTO TANJIRO'S HEART{\r} 💉",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "His flesh instantly mutated—horns erupted through his skull, spine blades tore from his back, and his kind eyes turned blood-red.",
        "MonsterCard",
        r"HORNS & SPINE BLADES ERUPT: {\c&H00FFFF00\3c&H000000FF\blur3\bord3}KIND EYES TURN BLOOD-RED{\r} 💀",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "Then came the ultimate horror: the morning sun hit Tanjiro's skin... and he didn't burn! Because he mastered Sun Breathing, he became immune to sunlight!",
        "SunCard",
        r"SUNLIGHT HITS HIS SKIN: {\c&H0000FFFF\3c&H000080FF\blur5\bord5}HE CONQUERED THE SUN{\r}! ☀️🔥",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "He was completely immortal. When Inosuke raised his swords to stop him, he broke down weeping: 'I can't do it... he's our Tanjiro!'",
        "TragicCard",
        r"INOSUKE WEEPING: {\c&H00FFFFFF\3c&H00FF80FF\blur4\bord4}'I CAN'T DO IT... HE'S OUR TANJIRO!'{\r} ⚔️😭",
        NARRATOR_RATE, NARRATOR_PITCH, 1.2  # 1.2s dramatic breathing pause before line
    ),
    (
        "The kindest boy in anime was turned into an unkillable god of destruction.",
        "ClimaxCard",
        r"THE KINDEST HERO: {\c&H000000FF\3c&H0000FFFF\blur5\bord4}AN UNKILLABLE GOD OF DESTRUCTION{\r} 🩸",
        NARRATOR_RATE, NARRATOR_PITCH, 0.0
    ),
    (
        "Subscribe to Dark Matters for more hidden anime secrets!",
        "CuteOutro",
        r"{\c&H00FFFFFF\3c&H00FF80FF\blur3\bord3}SUBSCRIBE TO DARK MATTERS FOR MORE SECRETS! ❤️{\r}",
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
Style: ExplainCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: MysteryCard,Arial Black,48,&H00FFFF00,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: MonsterCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: SunCard,Arial Black,50,&H00FFFFFF,&H00FF80FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: TragicCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
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
    voice_wav = os.path.join(AUDIO_DIR, "prj080_voice.wav")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", voice_wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    ass_path = os.path.join(AUDIO_DIR, "prj080_subtitles.ass")
    build_ass(timings, ass_path)
    return voice_wav, ass_path, timings, cursor


def mix_audio(voice_wav: str, total_dur: float, timings: list) -> str:
    master_wav = os.path.join(AUDIO_DIR, "prj080_master_mix.wav")

    # SFX timing points in milliseconds:
    riser_0_ms = int(timings[0][0] * 1000)
    heartbeat_2_ms = int(timings[2][0] * 1000)
    boom_3_ms = int(timings[3][0] * 1000)
    whoosh_4_ms = int(timings[4][0] * 1000)
    warmboom_4_ms = int((timings[4][0] + 0.3) * 1000)
    heartbeat_5_ms = int((timings[5][0] - 1.0) * 1000)  # During the breathing silence!

    # Complex audio filter:
    # 1. Narrator voice with clarity EQ and compression
    # 2. Cinematic tension drone (intro through mutation)
    # 3. Tragic sad piano (heartbreak & emotional climax)
    # 4. Cinematic SFX (heartbeat during silence, explosion of spine blades, sub boom for sunlight immunity)
    filter_complex = (
        "[0:a]highpass=f=80,equalizer=f=2800:t=q:w=1.2:g=2.0,highshelf=f=7500:g=-1.5,acompressor=threshold=-16dB:ratio=2.4:attack=12:release=140,volume=1.40[v];"
        f"[1:a]atrim=start=0:duration={min(total_dur, 28.0):.2f},asetpts=PTS-STARTPTS,highpass=f=40,lowpass=f=7000,"
        f"afade=t=in:st=0:d=1.0,afade=t=out:st={max(0, min(total_dur, 28.0)-2.0):.2f}:d=2.0,volume=0.045[bgm1];"
        f"[2:a]atrim=start=22:duration={total_dur-22:.2f},asetpts=PTS-STARTPTS,highpass=f=60,lowpass=f=8000,"
        f"afade=t=in:st=0:d=2.0,afade=t=out:st={max(0, total_dur-22-1.5):.2f}:d=1.5,volume=0.055[bgm2];"
        f"[3:a]adelay={riser_0_ms}|{riser_0_ms},volume=0.25[s_riser];"
        f"[4:a]adelay={heartbeat_2_ms}|{heartbeat_2_ms},volume=0.35[s_hb2];"
        f"[5:a]adelay={boom_3_ms}|{boom_3_ms},volume=0.30[s_boom3];"
        f"[6:a]adelay={whoosh_4_ms}|{whoosh_4_ms},volume=0.22[s_wh4];"
        f"[7:a]adelay={warmboom_4_ms}|{warmboom_4_ms},volume=0.28[s_wbm4];"
        f"[8:a]adelay={heartbeat_5_ms}|{heartbeat_5_ms},volume=0.40[s_hb5];"
        "[v][bgm1][bgm2][s_riser][s_hb2][s_boom3][s_wh4][s_wbm4][s_hb5]amix=inputs=9:duration=first:dropout_transition=0:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=6,alimiter=limit=0.94[out]"
    )
    subprocess.run([
        FFMPEG, "-y",
        "-i", voice_wav,
        "-i", BGM_DRONE,
        "-i", BGM_PIANO,
        "-i", SFX_RISER,
        "-i", SFX_HEARTBEAT,
        "-i", SFX_BOOM,
        "-i", SFX_WHOOSH,
        "-i", SFX_WARM_BOOM,
        "-i", SFX_HEARTBEAT,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        master_wav,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return master_wav


def compile_real_footage(master_wav: str, ass_path: str, total_dur: float, timings: list):
    clip_hero = os.path.join(WORK_DIR, "tanjiro_kind_hero.mp4")
    clip_sunrise = os.path.join(WORK_DIR, "dkt_sunrise_animation.mp4")
    clip_twixtor = os.path.join(WORK_DIR, "dkt_twixtor_4k.mp4")
    clip_ultra = os.path.join(WORK_DIR, "dkt_4k_ultra.mp4")

    used_sources = [clip_hero, clip_sunrise, clip_twixtor, clip_ultra]
    for src in used_sources:
        assert os.path.exists(src), f"Missing media source: {src}"
    bridge.audit_real_world_scenes([
        {"media_kind": "video", "path": clip_hero, "width": 1920, "height": 1080},
        {"media_kind": "video", "path": clip_sunrise, "width": 1920, "height": 1080},
        {"media_kind": "video", "path": clip_twixtor, "width": 1920, "height": 1080},
        {"media_kind": "video", "path": clip_ultra, "width": 1920, "height": 1080},
    ])
    bridge.verify_and_register_unique_assets("PRJ-080", used_sources)

    # 8 rhythmic video cuts matching exactly with the story beats and pauses
    cut_specs = [
        # Cut 0: Kind Tanjiro smiling (Hook - shock revelation)
        (clip_hero, 7.5, timings[0][1] - timings[0][0], 0.50, "Kind Tanjiro smiling"),
        # Cut 1: Muzan dissolving in sunrise (Muzan's dying choice)
        (clip_sunrise, 3.5, timings[1][1] - timings[1][0], 0.50, "Muzan dissolving in sunrise"),
        # Cut 2: Muzan blood injecting into Tanjiro's heart (Demonic rebirth)
        (clip_sunrise, 24.5, timings[2][1] - timings[2][0], 0.50, "Muzan blood injecting into Tanjiro"),
        # Cut 3: Demonic horns and spine blades erupting (Mutated monster)
        (clip_twixtor, 7.5, timings[3][1] - timings[3][0], 0.50, "Horns and spine blades erupting"),
        # Cut 4: Sunlight hitting Demon Tanjiro - immune to sun (Solar climax)
        (clip_ultra, 14.5, timings[4][1] - timings[4][0], 0.50, "Sunlight on Tanjiro skin - immune"),
        # Cut 5: Inosuke crying with dual swords (Heartbreak tragedy + silence)
        (clip_sunrise, 57.0, timings[5][1] - timings[5][0] + 1.2, 0.50, "Inosuke weeping with swords"),
        # Cut 6: Demon King Tanjiro standing alone in destruction (God of destruction)
        (clip_twixtor, 21.0, timings[6][1] - timings[6][0], 0.50, "DKT standing in destruction"),
        # Cut 7: Peaceful smiling Tanjiro + cute outro (Peaceful resolution)
        (clip_hero, 24.5, timings[7][1] - timings[7][0] + 0.25, 0.50, "Peaceful Tanjiro smile + Cute outro"),
    ]

    temp_segs = []
    os.makedirs(os.path.join(WORK_DIR, "segs"), exist_ok=True)

    for idx, (src, st, dur, crop_x, label) in enumerate(cut_specs):
        seg_mp4 = os.path.join(WORK_DIR, "segs", f"seg_{idx:02d}.mp4")
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:1920:(in_w-out_w)*{crop_x}:0,eq=contrast=1.08:saturation=1.16:gamma=1.02,fps=30,format=yuv420p"
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
        qa_img = os.path.join(ART_DIR, f"qa_prj080_{ts_tag}.jpg")
        subprocess.run([FFMPEG, "-y", "-ss", f"{ts:.2f}", "-i", FINAL_MP4, "-frames:v", "1", qa_img],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("QA_FRAME:", qa_img)


def main():
    voice_wav, ass_path, timings, total_dur = asyncio.run(synth_voice_and_ass())
    print(f"Voiceover synthesized: {total_dur:.2f}s across {len(timings)} beats (One voice: Ava)")
    master_wav = mix_audio(voice_wav, total_dur, timings)
    compile_real_footage(master_wav, ass_path, total_dur, timings)
    print("PRJ-080 BUILD COMPLETE:", FINAL_MP4)


if __name__ == "__main__":
    main()

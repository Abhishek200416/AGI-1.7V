import asyncio
import datetime
import json
import os
import subprocess
import sys
import edge_tts

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\abhis\Projects\IVA\studio\system")
import iva_video_bridge as bridge

BASE_DIR = r"c:\Users\abhis\Downloads\ytsss\AI_MEDIA_STUDIO"
WORK_DIR = os.path.join(BASE_DIR, "video", "prj077_couple_candid")
AUDIO_DIR = os.path.join(BASE_DIR, "audio", "prj077_couple_candid")
FINAL_MP4 = os.path.join(BASE_DIR, "video", "final_exports", "prj077_couple_candid_short.mp4")
ART_DIR = r"C:\Users\abhis\.gemini\antigravity\brain\93384ca3-839f-48d8-82bc-403889e3d4bc"

FFMPEG = r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffprobe.exe"

# Wholesome warm chillout track
BGM_TRACK = os.path.join(BASE_DIR, "music", "compositions", "mixkit_chillout_1_443.mp3")
SFX_SHUTTER = os.path.join(BASE_DIR, "music", "sound_effects", "slide_click.wav")
SFX_WHOOSH = os.path.join(BASE_DIR, "music", "sound_effects", "whoosh_transition.wav")
SFX_HEARTBEAT = os.path.join(BASE_DIR, "music", "sound_effects", "heartbeat_thud.wav")
SFX_WARM_BOOM = os.path.join(BASE_DIR, "music", "sound_effects", "warm_sub_boom.wav")

# Voice casting according to operator directives:
# Male voice for cute setups, relatable moments, and scientific facts
MALE_VOICE = "en-US-ChristopherNeural"
MALE_RATE = "+8%"
MALE_PITCH = "+0Hz"

# Female voice for interesting psychological explanations
FEMALE_VOICE = "en-US-AvaNeural"
FEMALE_RATE = "+12%"
FEMALE_PITCH = "+0Hz"

# Cute female outro voice for CTA
OUTRO_VOICE = "en-US-AnaNeural"
OUTRO_RATE = "+5%"
OUTRO_PITCH = "+8Hz"

BEATS = [
    (
        "Ever notice why couples look so stiff taking photos... until one of them whispers something silly?",
        "CuteHook",
        r"WHY COUPLES LOOK AWKWARD {\c&H0000FFFF}UNTIL THEY WHISPER...{\r} 📸",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "Instantly, the awkward poses vanish, and pure uncontrollable laughter takes over!",
        "CuteHook",
        r"AWKWARD POSES VANISH: {\c&H00FF80FF}PURE UNCONTROLLABLE LAUGHTER{\r}!",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "In psychology, this is the difference between a staged Pan-Am smile and a genuine Duchenne smile.",
        "CompareCard",
        r"STAGED SMILE vs {\c&H0000FFFF}GENUINE DUCHENNE SMILE{\r}",
        FEMALE_VOICE, FEMALE_RATE, FEMALE_PITCH
    ),
    (
        "When told to smile, only mouth muscles move. Your brain knows it is fake, so the photo feels completely frozen.",
        "ExplainCard",
        r"FORCED SMILES FREEZE: {\c&H0000FFFF}BRAIN KNOWS IT'S STAGED{\r}",
        FEMALE_VOICE, FEMALE_RATE, FEMALE_PITCH
    ),
    (
        "But when couples share a candid laugh, something miraculous happens: interpersonal autonomic synchrony.",
        "ScienceCard",
        r"SCIENCE: {\c&H00FF80FF}INTERPERSONAL AUTONOMIC SYNCHRONY{\r} ✨",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "Their heart rates literally synchronize to the exact same rhythm, and stress hormones plummet by thirty percent!",
        "ScienceCard",
        r"HEARTRATES SYNCHRONIZE: {\c&H0000FFFF}STRESS DROPS BY 30%{\r}!",
        MALE_VOICE, MALE_RATE, MALE_PITCH
    ),
    (
        "That is why the best couple photos are never the perfect poses—they are the blurry, laughing memories.",
        "WarmClimax",
        r"THE BEST PHOTOS ARE ALWAYS {\c&H00FF80FF}THE CANDID OUTTAKES{\r} ❤️",
        MALE_VOICE, MALE_RATE, MALE_PITCH
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
Style: CuteHook,Arial Black,48,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: CompareCard,Arial Black,48,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: ExplainCard,Arial Black,48,&H00FFFF00,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: ScienceCard,Arial Black,48,&H00FF80FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
Style: WarmClimax,Arial Black,50,&H00FFFFFF,&H00FF80FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,340,1
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
    seg_wavs = []
    timings = []
    cursor = 0.0
    for idx, (spoken, style, caption, voice, rate, pitch) in enumerate(BEATS):
        raw_mp3 = os.path.join(AUDIO_DIR, f"beat_{idx:02d}.mp3")
        raw_wav = os.path.join(AUDIO_DIR, f"beat_{idx:02d}.wav")

        if not (os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 1000):
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
    voice_wav = os.path.join(AUDIO_DIR, "prj077_voice.wav")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", voice_wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    ass_path = os.path.join(AUDIO_DIR, "prj077_subtitles.ass")
    build_ass(timings, ass_path)
    return voice_wav, ass_path, timings, cursor


def mix_audio(voice_wav: str, total_dur: float, timings: list) -> str:
    master_wav = os.path.join(AUDIO_DIR, "prj077_master_mix.wav")

    # SFX timing points in milliseconds:
    shutter_hook_ms = int(timings[0][0] * 1000)
    whoosh_turn_ms = int(timings[1][0] * 1000)
    shutter_compare_ms = int(timings[2][0] * 1000)
    heartbeat_ms = int(timings[5][0] * 1000)
    warm_climax_ms = int(timings[6][0] * 1000)

    # Master audio processing:
    # 1. Voice: Multi-voice (Christopher + Ava + Ana), EQ clarity, smooth compressor
    # 2. BGM: Relaxing chillout track ducked to -28 dBFS, smooth high-shelf dip at 4.2kHz
    # 3. SFX: Camera clicks and gentle heartbeat sync
    filter_complex = (
        "[0:a]highpass=f=80,equalizer=f=2800:t=q:w=1.2:g=1.8,highshelf=f=7500:g=-1.5,acompressor=threshold=-16dB:ratio=2.4:attack=12:release=140,volume=1.40[v];"
        f"[1:a]atrim=start=0:duration={total_dur:.2f},asetpts=PTS-STARTPTS,highpass=f=50,equalizer=f=2800:t=q:w=1.2:g=-4.0,highshelf=f=4200:g=-6.5,lowpass=f=8000,"
        f"afade=t=in:st=0:d=1.0,afade=t=out:st={max(0, total_dur-1.5):.2f}:d=1.5,volume=0.048[bgm];"
        f"[2:a]adelay={shutter_hook_ms}|{shutter_hook_ms},volume=0.22[s0];"
        f"[3:a]adelay={whoosh_turn_ms}|{whoosh_turn_ms},volume=0.18[w0];"
        f"[4:a]adelay={shutter_compare_ms}|{shutter_compare_ms},volume=0.20[s1];"
        f"[5:a]adelay={heartbeat_ms}|{heartbeat_ms},volume=0.25[hb];"
        f"[6:a]adelay={warm_climax_ms}|{warm_climax_ms},volume=0.22[wb];"
        "[v][bgm][s0][w0][s1][hb][wb]amix=inputs=7:duration=first:dropout_transition=0:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=6,alimiter=limit=0.94[out]"
    )
    subprocess.run([
        FFMPEG, "-y",
        "-i", voice_wav,
        "-i", BGM_TRACK,
        "-i", SFX_SHUTTER,
        "-i", SFX_WHOOSH,
        "-i", SFX_SHUTTER,
        "-i", SFX_HEARTBEAT,
        "-i", SFX_WARM_BOOM,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        master_wav,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return master_wav


def compile_real_footage(master_wav: str, ass_path: str, total_dur: float, timings: list):
    clip_laugh = os.path.join(WORK_DIR, "couple_laugh_posing.mp4")
    clip_park = os.path.join(WORK_DIR, "couple_park_sunset.mp4")

    used_sources = [clip_laugh, clip_park]
    for src in used_sources:
        assert os.path.exists(src), f"Missing real media source: {src}"
    bridge.audit_real_world_scenes([
        {"media_kind": "video", "path": clip_laugh, "width": 1920, "height": 1080},
        {"media_kind": "video", "path": clip_park, "width": 1920, "height": 1080},
    ])
    bridge.verify_and_register_unique_assets("PRJ-077", used_sources)

    # 8 rhythmic real-world video cuts matching exactly with the story beats
    # Each cut has start time in source clip and duration matched to voiceover
    cut_specs = [
        # Cut 0: Awkward posing setup (Male cute hook)
        ("video", clip_laugh, 32.0, timings[0][1] - timings[0][0], "Couple awkwardly trying to pose while photographer gives prompts"),
        # Cut 1: Whisper silly prompt -> instant laughter (Male cute hook)
        ("video", clip_laugh, 74.0, timings[1][1] - timings[1][0], "Photographer prompts whisper and both burst into big genuine smiles"),
        # Cut 2: Close-up laughing faces (Female comparison Pan-Am vs Duchenne)
        ("video", clip_laugh, 108.0, timings[2][1] - timings[2][0], "Close-up of couple laughing uncontrollably with genuine eye crinkles"),
        # Cut 3: Walking naturally in park (Female explanation)
        ("video", clip_park, 4.0, timings[3][1] - timings[3][0], "Couple strolling along scenic tree-lined park path"),
        # Cut 4: Lush canopy, holding hands & laughing (Male scientific fact)
        ("video", clip_park, 14.0, timings[4][1] - timings[4][0], "Lush bokeh framing, holding hands and sharing a tender laugh"),
        # Cut 5: Close embrace hand on chest (Male scientific fact: heart rates sync)
        ("video", clip_park, 43.0, timings[5][1] - timings[5][0], "Close-up romantic embrace with gentle sunlight"),
        # Cut 6: Golden hour sunset silhouette (Male warm climax)
        ("video", clip_park, 58.0, timings[6][1] - timings[6][0], "Romantic golden hour sunset silhouette with warm lens flare"),
        # Cut 7: Outro sweet look + CTA (Cute female outro)
        ("video", clip_park, 20.0, timings[7][1] - timings[7][0] + 0.25, "Tender smiles looking at each other + Cute subscription outro"),
    ]

    temp_segs = []
    os.makedirs(os.path.join(WORK_DIR, "segs"), exist_ok=True)

    for idx, (kind, src, st, dur, label) in enumerate(cut_specs):
        seg_mp4 = os.path.join(WORK_DIR, "segs", f"seg_{idx:02d}.mp4")
        # Center crop or left-bias crop for photoshoot behind-the-scenes
        crop_x = "(in_w-out_w)*0.22" if src == clip_laugh and idx in (1, 2) else "(in_w-out_w)*0.45" if src == clip_laugh else "(in_w-out_w)/2"
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:1920:{crop_x}:0,eq=contrast=1.06:saturation=1.14:gamma=1.02,fps=30,format=yuv420p"
        )
        cmd = [FFMPEG, "-y", "-ss", f"{st:.2f}", "-i", src, "-t", f"{dur:.3f}",
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

    for ts_tag, ts in [("02s", 2.0), ("15s", 15.0), ("28s", 28.0), ("climax", max(2.0, total_dur - 3.0))]:
        qa_img = os.path.join(ART_DIR, f"qa_prj077_{ts_tag}.jpg")
        subprocess.run([FFMPEG, "-y", "-ss", f"{ts:.2f}", "-i", FINAL_MP4, "-frames:v", "1", qa_img],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("QA_FRAME:", qa_img)


def main():
    voice_wav, ass_path, timings, total_dur = asyncio.run(synth_voice_and_ass())
    print(f"Voiceover synthesized: {total_dur:.2f}s across {len(timings)} beats (Christopher + Ava + Ana)")
    master_wav = mix_audio(voice_wav, total_dur, timings)
    compile_real_footage(master_wav, ass_path, total_dur, timings)
    print("PRJ-077 BUILD COMPLETE:", FINAL_MP4)


if __name__ == "__main__":
    main()

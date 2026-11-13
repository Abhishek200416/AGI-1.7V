import asyncio
import datetime
import json
import os
import re
import shutil
import sqlite3
import sys
import urllib.request
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.environ.get("IVA_STUDIO_DIR", os.path.join(str(os.path.expanduser("~")), "Downloads", "ytsss", "AI_MEDIA_STUDIO"))
PROJECT_ID = "PRJ-077"
PUBLISH_ID = "PUB-077"
CHANNEL_ID = "UCX3ccjtvn5S4S2Yutu55YWA"
USER_DATA = os.environ.get("CHROME_USER_DATA", os.path.join(str(os.path.expanduser("~")), "AppData", "Local", "ms-playwright-mcp", "mcp-chrome-08d3779"))
VIDEO_PATH = os.path.join(BASE_DIR, "video", "final_exports", "prj077_couple_candid_short.mp4")
TITLE = "Why Couples Look Awkward In Photos (Until 1 Silly Whisper!) 📸❤️ #Shorts #Psychology"
DESCRIPTION = (
    "Ever notice why couples look so stiff and awkward taking photos... until one of them whispers something silly?\n\n"
    "In psychology, this is the difference between a polite Pan-Am smile and a genuine Duchenne smile. "
    "When told to pose, only mouth muscles move—and your brain knows it's staged!\n\n"
    "But the instant couples share a candid laugh, something miraculous happens: interpersonal autonomic synchrony. "
    "Their heart rates literally synchronize to the exact same rhythm, and stress hormones plummet by thirty percent!\n\n"
    "That's why the best couple photos are never the perfect poses—they're the blurry, laughing memories where you can feel the warmth through the screen.\n\n"
    "Voice Casting:\n"
    "• Male Storyteller & Neuroscience: en-US-ChristopherNeural (+8%)\n"
    "• Psychological Explanations: en-US-AvaNeural (+12%)\n"
    "• Outro CTA: en-US-AnaNeural (+5%, +8Hz)\n\n"
    "Music: 'Chillout Acoustic Groove' (Mixkit Royalty-Free License)\n\n"
    "#Shorts #Love #Psychology #RelationshipGoals #CandidPhotos #ScienceOfLove #CoupleGoals #CuteMoments #DidYouKnow"
)
DB_PATH = os.path.join(BASE_DIR, "system", "omega_production.db")
QUEUE_PATH = os.path.join(BASE_DIR, "system", "staging_queue.json")


def verify_http_live(vid_id: str) -> tuple[bool, str]:
    url = f"https://www.youtube.com/watch?v={vid_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        m_title = re.search(r"<title>(.*?)</title>", html, re.S)
        page_title = m_title.group(1).strip() if m_title else ""
        is_live = ("Couples" in page_title or "Awkward" in page_title or "Photos" in page_title or "Whisper" in page_title) and ('"isPrivate":false' in html or '"status":"OK"' in html)
        return is_live, page_title
    except Exception as e:
        return False, str(e)


def finalize_records(vid_id: str, published_url: str) -> None:
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now_ist = now_utc.astimezone(ist).strftime("%I:%M:%S %p IST")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO publishing_history (
            publish_id, project_id, channel_id, video_id, youtube_url, title, description, visibility, status, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (PUBLISH_ID, PROJECT_ID, CHANNEL_ID, vid_id, published_url, TITLE, DESCRIPTION, "Public", "PUBLISHED", now_iso),
    )
    cur.execute(
        """
        INSERT OR REPLACE INTO projects (
            project_id, title, format, status, published_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (PROJECT_ID, TITLE, "Shorts", "PUBLISHED", now_iso),
    )
    conn.commit()
    conn.close()

    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8") as qf:
            qdata = json.load(qf)
        found = False
        for item in qdata:
            if item.get("project_id") == PROJECT_ID:
                item["status"] = "PUBLISHED"
                item["video_id"] = vid_id
                item["youtube_url"] = published_url
                item["published_ist"] = now_ist
                found = True
        if not found:
            qdata.append({
                "project_id": PROJECT_ID,
                "title": TITLE,
                "script": os.path.join(BASE_DIR, "system", "publish_project_077.py"),
                "video": VIDEO_PATH,
                "status": "PUBLISHED",
                "published_ist": now_ist,
                "video_id": vid_id,
                "youtube_url": published_url,
            })
        with open(QUEUE_PATH, "w", encoding="utf-8") as qf:
            json.dump(qdata, qf, indent=2, ensure_ascii=False)
        print(f"[QUEUE] Updated staging_queue.json for {PROJECT_ID} ({now_ist})", flush=True)

    # Clean intermediate segments
    for p_del in [
        os.path.join(BASE_DIR, "audio", "prj077_couple_candid"),
        os.path.join(BASE_DIR, "video", "prj077_couple_candid", "segs"),
    ]:
        try:
            if os.path.isdir(p_del):
                shutil.rmtree(p_del)
            elif os.path.isfile(p_del):
                os.remove(p_del)
            print(f"[STORAGE PURGE] Removed {p_del}", flush=True)
        except Exception as e:
            print(f"[STORAGE WARN] Could not remove {p_del}: {e}", flush=True)


async def finalize_draft_to_public(page, vid_id: str) -> None:
    print(f"[DRAFT FINALIZER] Navigating to edit draft: https://studio.youtube.com/video/{vid_id}/edit", flush=True)
    await page.goto(f"https://studio.youtube.com/video/{vid_id}/edit", wait_until="domcontentloaded")
    await asyncio.sleep(4)

    edit_draft_btn = page.locator("text='Edit draft'").locator("visible=true").first
    if await edit_draft_btn.count() > 0:
        await edit_draft_btn.click()
        print("[DRAFT FINALIZER] Clicked Edit draft button", flush=True)
        await asyncio.sleep(3)

    not_kids = page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').locator("visible=true").first
    if await not_kids.count() > 0:
        await not_kids.scroll_into_view_if_needed()
        if (await not_kids.get_attribute("aria-checked")) != "true":
            await not_kids.click(force=True)
            print("[DRAFT FINALIZER] Checked Not Made For Kids", flush=True)

    pub_radio = page.locator('tp-yt-paper-radio-button[name="PUBLIC"]').locator("visible=true").first
    for step in range(1, 5):
        if await pub_radio.count() > 0:
            break
        nxt = page.locator("#next-button").locator("visible=true").first
        if await nxt.count() > 0:
            await nxt.click()
            print(f"[DRAFT FINALIZER] Clicked Next ({step})", flush=True)
            await asyncio.sleep(2.0)

    if await pub_radio.count() > 0:
        await pub_radio.wait_for(state="visible", timeout=15000)
        if (await pub_radio.get_attribute("aria-checked")) != "true":
            await pub_radio.click(force=True)
            print("[DRAFT FINALIZER] Selected Public radio", flush=True)

    save_btn = page.locator("#done-button, #save-button").locator("visible=true").first
    if await save_btn.count() > 0:
        await save_btn.click()
        print("[DRAFT FINALIZER] Clicked Save / Publish", flush=True)
        await asyncio.sleep(6)


async def main():
    assert os.path.isfile(VIDEO_PATH), f"Video missing: {VIDEO_PATH}"
    size_mb = os.path.getsize(VIDEO_PATH) / (1024 * 1024)
    print(f"[PREFLIGHT] {VIDEO_PATH} ({size_mb:.2f} MB), title len={len(TITLE)}", flush=True)

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            USER_DATA,
            channel="chrome",
            headless=False,
            args=[
                "--profile-directory=Profile 3",
                "--window-position=-32000,-32000",
                "--window-size=1280,1000",
            ],
        )
        try:
            # 1. Anti-duplicate check
            chk_page = await ctx.new_page()
            await chk_page.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short", wait_until="domcontentloaded")
            await asyncio.sleep(5)
            rows = chk_page.locator("ytcp-video-row")
            row_count = await rows.count()
            for idx in range(min(4, row_count)):
                txt = await rows.nth(idx).inner_text()
                if "Couples Look Awkward" in txt or "Silly Whisper" in txt:
                    print(f"[DUPLICATE GUARD] Already present in Studio row {idx}: {txt[:120]}", flush=True)
                    m_vid = re.search(r"/video/([A-Za-z0-9_-]{11})/", await rows.nth(idx).inner_html())
                    if m_vid:
                        vid = m_vid.group(1)
                        if "Draft" in txt:
                            print(f"[RECOVERY] Found existing Draft for {vid}, finalizing...", flush=True)
                            await finalize_draft_to_public(chk_page, vid)
                            live_ok, pt = verify_http_live(vid)
                            if live_ok:
                                finalize_records(vid, f"https://youtube.com/shorts/{vid}")
                                return
                    raise RuntimeError("PRJ-077 title already found in Studio rows — aborting duplicate upload")
            await chk_page.close()

            # 2. Upload via ?d=ud
            page = await ctx.new_page()
            await page.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/upload?d=ud", wait_until="domcontentloaded")
            file_input = page.locator("input[type='file']").first
            await file_input.wait_for(state="attached", timeout=35000)
            await file_input.set_input_files(VIDEO_PATH)
            print("[UPLOAD] File attached, waiting for metadata dialog...", flush=True)

            title_box = page.locator("ytcp-social-suggestions-textbox#title-textarea div#textbox").first
            await title_box.wait_for(state="visible", timeout=45000)
            await title_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.keyboard.insert_text(TITLE)

            desc_box = page.locator("ytcp-social-suggestions-textbox#description-textarea div#textbox").first
            await desc_box.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.keyboard.insert_text(DESCRIPTION)
            print("[METADATA] Title & description populated", flush=True)

            not_kids = page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').locator("visible=true").first
            await not_kids.scroll_into_view_if_needed()
            if (await not_kids.get_attribute("aria-checked")) != "true":
                await not_kids.click(force=True)

            vid_id = None
            for _ in range(25):
                html_snippet = await page.content()
                m = re.search(r"https://youtu\.be/([A-Za-z0-9_-]{11})", html_snippet)
                if not m:
                    m = re.search(r"https://youtube\.com/shorts/([A-Za-z0-9_-]{11})", html_snippet)
                if m:
                    vid_id = m.group(1)
                    break
                await asyncio.sleep(1.5)
            print(f"[VIDEO ID] Detected: {vid_id}", flush=True)

            for _ in range(40):
                status_txt = await page.locator("span.progress-label").first.inner_text() if await page.locator("span.progress-label").count() else ""
                if "100%" in status_txt or "Checks complete" in status_txt or "Processing" in status_txt or "Upload complete" in status_txt:
                    print(f"[UPLOAD STATUS] {status_txt}", flush=True)
                    break
                await asyncio.sleep(2.0)

            pub_radio = page.locator('tp-yt-paper-radio-button[name="PUBLIC"]').locator("visible=true").first
            for step in range(1, 5):
                if await pub_radio.count() > 0:
                    break
                nxt = page.locator("#next-button").locator("visible=true").first
                await nxt.wait_for(state="visible", timeout=20000)
                await nxt.click()
                print(f"[STEP] Clicked Next ({step})", flush=True)
                await asyncio.sleep(2.0)

            await pub_radio.wait_for(state="visible", timeout=25000)
            if (await pub_radio.get_attribute("aria-checked")) != "true":
                await pub_radio.click(force=True)
            print("[VISIBILITY] Selected PUBLIC", flush=True)
            await asyncio.sleep(1.5)

            if not vid_id:
                html_snippet = await page.content()
                m = re.search(r"(?:youtu\.be/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})", html_snippet)
                if m:
                    vid_id = m.group(1)

            done_btn = page.locator("#done-button").locator("visible=true").first
            await done_btn.wait_for(state="visible", timeout=15000)
            await done_btn.click()
            print("[PUBLISH] Clicked Publish (#done-button)", flush=True)

            for i in range(15):
                await asyncio.sleep(2.0)
                body_txt = await page.locator("body").inner_text()
                if "Video published" in body_txt or "Share a link" in body_txt:
                    print(f"[CONFIRM] Saw publish confirmation at t={2*(i+1)}s", flush=True)
                    break

            if not vid_id:
                await page.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short", wait_until="domcontentloaded")
                await asyncio.sleep(5)
                row_html = await page.locator("ytcp-video-row").first.inner_html()
                m = re.search(r"/video/([A-Za-z0-9_-]{11})/", row_html)
                if m:
                    vid_id = m.group(1)

            assert vid_id, "Failed to extract published YouTube video ID"
            shorts_url = f"https://youtube.com/shorts/{vid_id}"
            print(f"[PUBLISHED URL] {shorts_url}", flush=True)

            # Check if immediately public
            live_ok = False
            page_title = ""
            for attempt in range(6):
                live_ok, page_title = verify_http_live(vid_id)
                if live_ok:
                    break
                print(f"[VERIFY] Attempt {attempt+1}/6: live={live_ok}, title='{page_title}'. Waiting 4s...", flush=True)
                await asyncio.sleep(4.0)

            if not live_ok:
                print(f"[FINALIZER NEEDED] Video {vid_id} might still be in Draft, running draft finalizer...", flush=True)
                await finalize_draft_to_public(page, vid_id)
                live_ok, page_title = verify_http_live(vid_id)
                print(f"[FINAL VERIFY] live={live_ok}, title='{page_title}'", flush=True)

            finalize_records(vid_id, shorts_url)
            print(f"[PUBLISH 077] 100% COMPLETE & LIVE: {shorts_url}", flush=True)

        finally:
            await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())

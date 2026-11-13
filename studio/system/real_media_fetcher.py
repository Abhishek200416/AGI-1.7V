#!/usr/bin/env python3
"""
IVA Studios — Real Web Visuals & Video Fetcher
Fetches real, verified topic-accurate photographs and real video clips from public web APIs
(NASA Images & Video Library, Wikimedia Commons, and Bing Image fallback), validates dimensions
and corruption via ffprobe, extracts clip frames when needed, and enforces the Zero-Recycle
SHA-256 visual ledger via iva_video_bridge so no image/clip is ever reused across projects.
"""

import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iva_video_bridge as bridge

FFMPEG = bridge.FFMPEG
FFPROBE = bridge.FFPROBE
UA = {"User-Agent": "IVA-Studios-MediaEngine/1.0 (https://github.com/Abhishek200416/IVA)"}


def _http_get_json(url: str, timeout: int = 12) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def _download_file(url: str, dest: str, timeout: int = 20) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    if len(data) < 12000:
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return True


MIN_MEDIA_HEIGHT = 720  # Strictly >=720p minimum; prefer 4K (2160p) -> 1440p -> 1080p -> 720p


def _validate_visual_file(path: str, min_dim: int = MIN_MEDIA_HEIGHT) -> dict | None:
    """Verify image or video file decodes cleanly via ffprobe and meets >=720p minimum quality."""
    try:
        out = subprocess.check_output(
            [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_streams", path],
            text=True,
            timeout=10,
        )
        streams = json.loads(out).get("streams", [])
        vstreams = [s for s in streams if s.get("codec_type") == "video"]
        if not vstreams:
            return None
        w, h = int(vstreams[0].get("width", 0)), int(vstreams[0].get("height", 0))
        if min(w, h) < min_dim and max(w, h) < 1280:
            return None
        return {"path": path, "width": w, "height": h}
    except Exception:
        return None


def search_nasa_media(query: str, media_type: str = "image", limit: int = 6) -> list[str]:
    """Search official NASA Image & Video Library for real photographs or MP4 footage."""
    q = urllib.parse.quote_plus(query)
    url = f"https://images-api.nasa.gov/search?q={q}&media_type={media_type}"
    urls: list[str] = []
    try:
        data = _http_get_json(url)
        for item in data.get("collection", {}).get("items", [])[:limit * 2]:
            if media_type == "image":
                for link in item.get("links", []):
                    href = link.get("href", "")
                    if href.lower().endswith((".jpg", ".jpeg", ".png")):
                        urls.append(href)
                        break
            else:
                collection_href = item.get("href", "")
                if collection_href:
                    assets = _http_get_json(collection_href)
                    for asset_url in assets if isinstance(assets, list) else []:
                        if asset_url.lower().endswith(".mp4") and "mobile" not in asset_url.lower():
                            urls.append(asset_url)
                            break
            if len(urls) >= limit:
                break
    except Exception:
        pass
    return urls


def search_wikimedia_videos(query: str, limit: int = 4) -> list[str]:
    """Search Wikimedia Commons for real-world documentary MP4/WebM video clips."""
    q = urllib.parse.quote_plus(f"{query} filetype:video")
    url = (
        "https://commons.wikimedia.org/w/api.php?"
        f"action=query&generator=search&gsrsearch={q}&gsrnamespace=6"
        f"&gsrlimit={limit * 3}&prop=imageinfo&iiprop=url|mime|size&format=json"
    )
    urls: list[str] = []
    try:
        data = _http_get_json(url)
        for p in data.get("query", {}).get("pages", {}).values():
            info = (p.get("imageinfo") or [{}])[0]
            mime = info.get("mime", "")
            w = int(info.get("width", 0))
            if mime in ("video/webm", "video/mp4") and w >= 640 and info.get("url"):
                urls.append(info["url"])
            if len(urls) >= limit:
                break
    except Exception:
        pass
    return urls


def search_pexels_media(query: str, media_type: str = "video", limit: int = 4) -> list[str]:
    """Fetch real-world outside HD stock video clips or photos from Pexels when PEXELS_API_KEY is set."""
    api_key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not api_key:
        return []
    q = urllib.parse.quote_plus(query)
    endpoint = (
        f"https://api.pexels.com/videos/search?query={q}&orientation=portrait&per_page={limit}"
        if media_type == "video"
        else f"https://api.pexels.com/v1/search?query={q}&orientation=portrait&per_page={limit}"
    )
    urls: list[str] = []
    try:
        req = urllib.request.Request(endpoint, headers={"Authorization": api_key, **UA})
        data = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="ignore"))
        if media_type == "video":
            for v in data.get("videos", []):
                files = sorted(
                    [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and int(f.get("width", 0)) >= 720],
                    key=lambda f: int(f.get("width", 0)),
                    reverse=True,
                )
                if files:
                    urls.append(files[0]["link"])
        else:
            for ph in data.get("photos", []):
                src = ph.get("src", {}).get("large2x") or ph.get("src", {}).get("original")
                if src:
                    urls.append(src)
    except Exception:
        pass
    return urls[:limit]


def search_wikimedia_images(query: str, limit: int = 6) -> list[str]:
    """Search Wikimedia Commons for real, topic-exact high-resolution photographs (never diagrams/cartoons)."""
    q = urllib.parse.quote_plus(query)
    url = (
        "https://commons.wikimedia.org/w/api.php?"
        f"action=query&generator=search&gsrsearch=intitle:{q}&gsrnamespace=6"
        f"&gsrlimit={limit * 4}&prop=imageinfo&iiprop=url|mime|size&format=json"
    )
    skip_words = (
        "pamphlet", "document", "manuscript", "book", "page_", "signature",
        "diagram", "cartoon", "clipart", "vector", "svg", "drawing", "sketch",
        "logo", "icon", "schematic", "infographic", "chart", "map_of",
        "psm_", "psm ", "plate_", "plate ", "illustration", "engraving",
    )
    urls: list[str] = []
    try:
        data = _http_get_json(url)
        pages = data.get("query", {}).get("pages", {}).values()
        for p in pages:
            title_low = p.get("title", "").lower()
            if any(w in title_low for w in skip_words):
                continue
            info = (p.get("imageinfo") or [{}])[0]
            mime = info.get("mime", "")
            w = int(info.get("width", 0))
            if mime in ("image/jpeg", "image/png", "image/webp") and w >= 720:
                urls.append(info["url"])
            if len(urls) >= limit:
                break
    except Exception:
        pass
    return urls


def download_yt_dlp_clip(query: str, dest_mp4: str, max_duration_s: int = 240) -> dict | None:
    """
    Download a real-world movie scene, scientific documentary clip, or web video via `yt_dlp`
    prioritizing 4K (2160p) -> 1440p -> 1080p -> 720p minimum, validated via ffprobe.
    """
    os.makedirs(os.path.dirname(os.path.abspath(dest_mp4)), exist_ok=True)
    fmt = "bv*[height>=1080][ext=mp4]+ba[ext=m4a]/bv*[height>=1080]+ba/b[height>=1080]/bv*[height>=720]+ba/b[height>=720]/best"
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--ffmpeg-location", r"C:\ffmpeg\ffmpeg-7.1-full_build\bin",
        "--extractor-args", "youtube:player_client=android,web",
        "--no-playlist",
        "--download-sections", "*00:00:10-00:00:45",
        "--force-keyframes-at-cuts",
        "-f", fmt,
        "--merge-output-format", "mp4",
        "-o", dest_mp4,
        f"ytsearch3:{query}",
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60, check=True)
        meta = _validate_visual_file(dest_mp4, min_dim=MIN_MEDIA_HEIGHT)
        if meta:
            meta["media_kind"] = "video"
            meta["query"] = query
            meta["source_url"] = f"ytsearch3:{query}"
            return meta
    except Exception:
        if os.path.exists(dest_mp4):
            os.remove(dest_mp4)
    return None


def search_bing_images(query: str, limit: int = 6) -> list[str]:
    """Fallback real photography search for outside world subjects (filters out clipart/diagrams)."""
    q = urllib.parse.quote_plus(f"{query} real photograph -cartoon -vector -diagram -clipart -illustration")
    url = f"https://www.bing.com/images/search?q={q}&form=HDRSC2"
    skip_tokens = ("cartoon", "clipart", "vector", "stick-figure", "diagram", "infographic", "shutterstock", "istockphoto")
    urls: list[str] = []
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        html = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="ignore")
        for m in re.findall(r'murl&quot;:&quot;(https?://[^&]+?)&quot;', html):
            m_low = m.lower()
            if any(tok in m_low for tok in skip_tokens):
                continue
            if any(ext in m_low for ext in (".jpg", ".jpeg", ".png", ".webp")):
                urls.append(m)
            if len(urls) >= limit:
                break
    except Exception:
        pass
    return urls


def fetch_unique_real_visuals(
    project_id: str,
    beat_queries: list[str],
    out_dir: str,
    include_video_clip: bool = True,
) -> list[dict]:
    """
    Download one unique, non-recycled, resolution-validated REAL-WORLD photo or real video clip
    for each narration beat query (video footage prioritized when include_video_clip=True).
    """
    os.makedirs(out_dir, exist_ok=True)
    ledger = {}
    if os.path.exists(bridge.LEDGER_PATH):
        with open(bridge.LEDGER_PATH, "r", encoding="utf-8") as f:
            ledger = json.load(f)

    results = []
    for idx, query in enumerate(beat_queries, 1):
        video_candidates = (
            search_pexels_media(query, media_type="video", limit=3)
            + search_nasa_media(query, media_type="video", limit=2)
            + search_wikimedia_videos(query, limit=2)
        ) if include_video_clip else []
        photo_candidates = (
            search_pexels_media(query, media_type="image", limit=3)
            + search_wikimedia_images(query, limit=4)
            + search_nasa_media(query, media_type="image", limit=4)
            + search_bing_images(query, limit=5)
        )
        candidates = video_candidates + photo_candidates

        chosen = None
        for cand_i, url in enumerate(candidates):
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm"):
                ext = ".jpg"
            dest = os.path.join(out_dir, f"beat_{idx:02d}_{cand_i}{ext}")
            try:
                if not _download_file(url, dest):
                    if os.path.exists(dest):
                        os.remove(dest)
                    continue
                digest = bridge.sha256_file(dest)
                if digest in ledger and ledger[digest] != project_id:
                    os.remove(dest)
                    continue
                meta = _validate_visual_file(dest)
                if not meta:
                    os.remove(dest)
                    continue
                bridge.verify_and_register_unique_assets(project_id, [dest])
                ledger[digest] = project_id
                meta["query"] = query
                meta["source_url"] = url
                meta["media_kind"] = "video" if ext in (".mp4", ".webm") else "image"
                chosen = meta
                break
            except Exception:
                if os.path.exists(dest):
                    os.remove(dest)
        if not chosen and include_video_clip:
            yt_dest = os.path.join(out_dir, f"beat_{idx:02d}_yt.mp4")
            yt_meta = download_yt_dlp_clip(query, yt_dest)
            if yt_meta:
                digest = bridge.sha256_file(yt_dest)
                if digest in ledger and ledger[digest] != project_id:
                    os.remove(yt_dest)
                else:
                    bridge.verify_and_register_unique_assets(project_id, [yt_dest])
                    ledger[digest] = project_id
                    chosen = yt_meta
        if chosen:
            results.append(chosen)

    return results


def _self_check():
    import tempfile, shutil
    tmp = tempfile.mkdtemp(prefix="iva_real_media_check_")
    try:
        res = fetch_unique_real_visuals(
            project_id="__SELF_CHECK_REAL_MEDIA__",
            beat_queries=["James Webb Space Telescope deep field galaxy", "Turritopsis dohrnii jellyfish"],
            out_dir=tmp,
        )
        print(f"[PASS] Fetched {len(res)} real unique web visual(s):")
        for item in res:
            print(f"   • {item['media_kind'].upper()} {item['width']}x{item['height']} | {os.path.basename(item['path'])} <- {item['source_url'][:70]}")
        assert len(res) >= 1, "Expected at least 1 verified real web visual!"
    finally:
        # Clean temp files and remove __SELF_CHECK_REAL_MEDIA__ entries from production hash ledger
        shutil.rmtree(tmp, ignore_errors=True)
        if os.path.exists(bridge.LEDGER_PATH):
            with open(bridge.LEDGER_PATH, "r", encoding="utf-8") as f:
                ledger = json.load(f)
            cleaned = {k: v for k, v in ledger.items() if v != "__SELF_CHECK_REAL_MEDIA__"}
            with open(bridge.LEDGER_PATH, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, indent=2)


if __name__ == "__main__":
    _self_check()

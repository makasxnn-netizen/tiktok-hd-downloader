import os
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/download")
def download():
    url = (request.form.get("url") or "").strip()
    if not url.startswith(("https://www.tiktok.com/", "https://tiktok.com/",
                           "https://vt.tiktok.com/", "https://vm.tiktok.com/")):
        return render_template("index.html", error="Pega un enlace válido de TikTok."), 400

    workdir = Path(tempfile.mkdtemp(prefix="tiktok_"))
    opts = {
        "outtmpl": str(workdir / "video.%(ext)s"),
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": 300 * 1024 * 1024,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            expected = Path(ydl.prepare_filename(info))
        candidates = list(workdir.glob("video.*"))
        if not candidates:
            return render_template("index.html", error="No encontré un archivo descargado. Prueba con otro enlace."), 502
        # Preferir el MP4 combinado si yt-dlp lo generó.
        file_path = next((p for p in candidates if p.suffix.lower() == ".mp4"), candidates[0])
        return send_file(file_path, as_attachment=True, download_name="tiktok_hd.mp4")
    except Exception:
        return render_template("index.html", error="No se pudo obtener el video. Puede ser privado, no disponible o requerir un método compatible."), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))

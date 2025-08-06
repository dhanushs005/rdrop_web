from flask import Flask, render_template, request, send_file
import subprocess
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
COOKIE_FILE = "youtube_cookies.txt"

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_video():
    try:
        video_url = request.form.get("url")
        resolution = request.form.get("resolution", "1080p")
        custom_filename = request.form.get("filename", "").strip()

        if not video_url:
            return "❌ No video URL provided."

        # Sanitize filename
        if custom_filename == "":
            custom_filename = f"video_{uuid.uuid4().hex[:8]}"

        output_path = os.path.join(DOWNLOAD_DIR, f"{custom_filename}.mp4")

        if not os.path.exists(COOKIE_FILE):
            return "❌ Cookie file not found on server."

        # Construct yt-dlp command
        command = [
            "yt-dlp",
            "--cookies", COOKIE_FILE,
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "-S", f"res:{resolution}",
            "-o", output_path,
            video_url
        ]

        print("🚀 Running command:", " ".join(command))

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("❌ yt-dlp error:", result.stderr)
            return f"❌ Download failed:\n\n{result.stderr}"

        if not os.path.exists(output_path):
            return "❌ Download failed. File not found."

        print(f"✅ Downloaded: {output_path}")
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print("❌ Exception:", str(e))
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))   
    app.run(debug=True, host='0.0.0.0', port=port)

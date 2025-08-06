from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid
import shutil

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
COOKIE_FILE = "youtube_cookies.txt"

# Ensure the download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    filename = request.form.get('filename', '').strip()

    if not video_url:
        return "❌ Error: No video URL provided."

    if not filename:
        filename = str(uuid.uuid4())  # Generate a unique name if not provided

    temp_dir = os.path.join(DOWNLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)

    out_path = os.path.join(temp_dir, f"{filename}.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': out_path,
        'merge_output_format': 'mp4',
        'quiet': True,
        'cookiefile': COOKIE_FILE,  # Use cookie file for authentication
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            final_filename = ydl.prepare_filename(info).replace("%(ext)s", "mp4")
        
        # Final file path
        downloaded_file = os.path.join(temp_dir, f"{filename}.mp4")
        
        # Find the actual downloaded file (yt-dlp might keep the original extension)
        for file in os.listdir(temp_dir):
            if file.startswith(filename):
                downloaded_file = os.path.join(temp_dir, file)
                break

        return send_file(downloaded_file, as_attachment=True)

    except Exception as e:
        return f"❌ Download failed: {str(e)}"

    finally:
        # Optional cleanup: Remove downloaded files after request
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid
import shutil

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
COOKIE_FILE = "youtube_cookies.txt"  # Make sure this file is included in your Render repo!

# Ensure the download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url', '').strip()
    filename = request.form.get('filename', '').strip()

    if not video_url:
        return "❌ Error: No video URL provided."

    # Generate a unique filename if not provided
    if not filename:
        filename = str(uuid.uuid4())

    # Temporary folder for this download
    temp_dir = os.path.join(DOWNLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)

    output_template = os.path.join(temp_dir, f"{filename}.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'quiet': True,
        'cookiefile': COOKIE_FILE,  # Used for YouTube login bypass
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            downloaded_file = downloaded_file.rsplit('.', 1)[0] + '.mp4'

        return send_file(downloaded_file, as_attachment=True)

    except Exception as e:
        return f"❌ Download failed: {str(e)}"

    finally:
        # Clean up temp folder after sending file
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Required for Render.com
    app.run(debug=True, host='0.0.0.0', port=port)

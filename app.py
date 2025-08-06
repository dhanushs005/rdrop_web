from flask import Flask, request, render_template, jsonify, send_file
import yt_dlp
import os
import tempfile
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    resolution = data.get('resolution', 'best')
    filename_raw = data.get('filename', 'RedDrop_Video')

    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    # Sanitize filename
    filename_safe = re.sub(r'[^\w\-_\. ]', '_', filename_raw)

    format_str = (
        f'bestvideo[height<={resolution}][ext=mp4]+bestaudio/best'
        if resolution != 'best' else 'bestvideo[ext=mp4]+bestaudio/best'
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, f"{filename_safe}.mp4")
        ydl_opts = {
            'format': format_str,
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'quiet': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                return send_file(output_path, as_attachment=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

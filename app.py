from flask import Flask, render_template, request, send_file, jsonify
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
        # Correctly get data from the JSON body of the request
        data = request.get_json()
        video_url = data.get("url")
        resolution = data.get("resolution", "best") # Changed default to 'best' to match frontend
        custom_filename = data.get("filename", "").strip()

        if not video_url:
            return jsonify({"error": "No video URL provided."}), 400

        # Sanitize filename
        if not custom_filename:
            # Use a more descriptive default filename if possible, otherwise fallback to UUID
            # NOTE: The current implementation will just use the default filename.
            # A more robust solution would be to get the title from the video info.
            custom_filename = f"RedDrop_Video.mp4" 
        else:
            # Add .mp4 extension if not present
            if not custom_filename.lower().endswith('.mp4'):
                custom_filename += ".mp4"

        output_path = os.path.join(DOWNLOAD_DIR, custom_filename)

        if not os.path.exists(COOKIE_FILE):
            # It's better to return a JSON error that the frontend can handle
            return jsonify({"error": "Cookie file not found on server."}), 500

        # Create the yt-dlp command.
        # This will download the video and audio streams separately and merge them.
        command = [
            "yt-dlp",
            "--cookies", COOKIE_FILE,
            "-f", f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]" if resolution != "best" else "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "-o", output_path,
            video_url
        ]
        
        # A simple fallback for resolutions:
        # 'best' will get the best video and audio available and merge them.
        # Other resolutions will try to get a video stream up to that resolution.

        print("🚀 Running command:", " ".join(command))

        # Using Popen for better control over stdout/stderr
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print("❌ yt-dlp error:", stderr)
            # Send a clear error message back to the user
            return jsonify({"error": f"Download failed: {stderr}"}), 500

        # Final check to ensure the file was created and is not empty
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            print("❌ Download failed. File not found or is empty after command execution.")
            return jsonify({"error": "Download failed. The final file was not created."}), 500

        print(f"✅ Downloaded: {output_path}")
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print("❌ Exception:", str(e))
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    # Set debug=False for production environments
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import tempfile
import os
app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route("/process-video", methods=["POST"])
def process_video():
    video_file = request.files.get("video")
    if not video_file:
        return "No video uploaded", 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        video_path = temp_video.name
        video_file.save(video_path)


    # itt meghivni a yolo-t
    return send_file(video_path, mimetype="video/mp4", as_attachment=True)




if __name__ == '__main__':
    app.run()

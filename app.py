from flask import Flask, request, send_from_directory, render_template, jsonify
import os
import cv2
import tempfile
from datetime import datetime
from detector import VehicleDetectionTracker
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
tracker = VehicleDetectionTracker()

os.makedirs("static/videos", exist_ok=True)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route("/process-video", methods=["POST"])
def process_video():
    video_file = request.files.get("video")
    
    if not video_file:
        return "No video uploaded", 400

    # Change the params of the detector based on the request
    tracker.speed_threshold = float(request.form.get('speed_threshold'))
    tracker.position_threshold = int(request.form.get('position_threshold'))
    tracker.time_threshold = int(request.form.get('time_threshold'))
    tracker.stationary_threshold = int(request.form.get('stationary_threshold'))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        video_path = temp_video.name
        video_file.save(video_path)

    output_filename = f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    output_path = os.path.join("static/videos", output_filename)
    number_of_vehicles_detected = process_video_file(video_path, output_path)

    if number_of_vehicles_detected:
        video_url = f"/videos/{output_filename}"
        return jsonify({"video_url": video_url, "number": tracker.car_count})
    else:
        return "Error processing video", 500


@app.route('/videos/<filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory('static/videos', filename, mimetype="video/mp4;codecs=vp9")


def process_video_file(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    tracker.car_count = 0

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS) or 20
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        tracker.process_frame(frame)
        resized_frame = cv2.resize(frame, (frame_width, frame_height))
        out.write(resized_frame)
        frame_count += 1

    cap.release()
    out.release()

    if os.path.getsize(output_path) == 0 or frame_count == 0:
        print("Error: No frames were written or file is empty.")
        return False

    print(f"Processed video saved to {output_path} with {frame_count} frames.")
    return True


if __name__ == '__main__':
    app.run(debug=True)

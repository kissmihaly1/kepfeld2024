import cv2
import base64
from collections import defaultdict
from ultralytics import YOLO
from datetime import datetime

class VehicleDetectionTracker:

    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)  # modell betoltese
        self.track_history = defaultdict(list)  # autok utvonala
        self.detected_vehicles = set()  # mar eszlelt jarmuvek azonositoja
        self.car_count = 0  # osszes eszlelt auto szama
        self.last_detection_time = {}  # utolso eszleles idopontja
        self.previous_centers = {}  # utolso eszlelt kozeppontok poz.
        self.last_printed_count = -1  # utolso kiirt jarmuszam

    # kepkocka base64 formatumba kodolasa
    def _encode_image_base64(self, image):
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode()
        return image_base64

    # aditt kepkocka feldolgozasa es auto felism.
    def process_frame(self, frame):
        response = {
            "number_of_vehicles_detected": 0,
            "original_frame_base64": None
        }

        # YOLO futtatasa kepkockan
        results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)
        if results and results[0] and results[0].boxes:
            boxes = results[0].boxes.xyxy.cpu()  # Bounding box lekerese YOLO-bol
            track_ids = results[0].boxes.id.int().cpu().tolist()  # egyedi ID
            classes = results[0].boxes.cls.int().cpu().tolist()  # osztaly ID

            current_time = datetime.now().timestamp()  # jelenlegi idobelyeg

            # osszes detektalt obj. feldolgozasa
            for box, track_id, class_id in zip(boxes, track_ids, classes):
                x1, y1, x2, y2 = box.int().tolist()  # Bounding box koord. kiszamitasa
                car_center_y = (y1 + y2) // 2

                # adott osztaly kocsi-e (2,3,5,7 osztaly)
                if class_id in [2, 3, 5, 7]:
                    if car_center_y >= 300:  # kuszob atlepese
                        time_since_last_detection = (current_time - self.last_detection_time.get(track_id, 0))
                        if time_since_last_detection > 5:  # 5mp limit
                            if track_id not in self.detected_vehicles:  # uj kocsi, jarmuszam nov.
                                self.detected_vehicles.add(track_id)
                                self.car_count += 1
                            self.last_detection_time[track_id] = current_time  # idopont frissites

                        # ID és keret megjelenitese
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f'ID: {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0),
                                    2)

            response["number_of_vehicles_detected"] = len(self.detected_vehicles)

        # szamlalo megjel.
        cv2.putText(frame, f'Total Vehicles Counted: {self.car_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    (255, 255, 255), 3)

        # kepkocka base64 formatumba kodolasa
        original_frame_base64 = self._encode_image_base64(frame)
        response["original_frame_base64"] = original_frame_base64

        return response

    # video feldolg. kepkockankent
    def process_video(self, video_path, display_size=(1280, 720)):
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # kepkocka auto felismereshez
            response = self.process_frame(frame)

            # kepkocka atmeretezese
            resized_frame = cv2.resize(frame, display_size)

            cv2.imshow("Vehicle Detection Tracker", resized_frame)

            # auto szamlalo kiiratasa
            if self.car_count != self.last_printed_count:
                print(f'Total Vehicles Counted: {self.car_count}')
                self.last_printed_count = self.car_count

            # 'q' billentyure vagy ablak bezaraskor kilep
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            # ablak be van-e zarva
            if cv2.getWindowProperty("Vehicle Detection Tracker", cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    video_path = 'videok/1_iranyban_1.mp4'
    tracker = VehicleDetectionTracker()
    tracker.process_video(video_path)

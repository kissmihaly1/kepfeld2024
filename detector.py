import cv2
import base64
from collections import defaultdict
from ultralytics import YOLO
from datetime import datetime
import numpy as np


class VehicleDetectionTracker:

    def __init__(self, model_path="yolov8n.pt", position_threshold=50, time_threshold=3, stationary_threshold=5):
        self.model = YOLO(model_path)  # modell betoltese
        self.track_history = defaultdict(list)  # autok utvonala
        self.detected_vehicles = set()  # mar eszlelt jarmuvek azonositoja
        self.car_count = 0  # osszes eszlelt auto szama
        self.last_detection_time = {}  # utolso eszleles idopontja
        self.previous_positions = {}  # utolso eszlelt kozeppontok poz.
        self.last_printed_count = -1  # utolso kiirt jarmuszam
        self.position_threshold = position_threshold  # min. poz. valtoztatas (pixelben)
        self.time_threshold = time_threshold  # min. idoelteres uj eszleleshez (mp-ben)
        self.stationary_threshold = stationary_threshold  # min. ido, amig az auto allhat

    # kepkocka base64 formatumba kodolasa
    def _encode_image_base64(self, image):
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode()
        return image_base64

    # szoveg arnyekkal
    def draw_text_with_shadow(self, image, text, position, font=cv2.FONT_HERSHEY_SIMPLEX,
                              font_scale=1.2, text_color=(255, 255, 255), shadow_color=(0, 0, 0), thickness=3):
        x, y = position

        # arnyek
        cv2.putText(image, text, (x + 2, y + 2), font, font_scale, shadow_color, thickness)

        # feher szoveg fole
        cv2.putText(image, text, (x, y), font, font_scale, text_color, thickness)

    # 2 poz. tavolsaganak kiszam.
    def calculate_distance(self, pos1, pos2):
        return np.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    # adott kepkocka feldolgozasa es auto felism.
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
                car_center = ((x1 + x2) // 2, (y1 + y2) // 2)

                # autok osztalya
                if class_id == 2:
                    # kocsi a detektalasi zonaban van
                    if car_center[1] >= 300:
                        time_since_last_detection = current_time - self.last_detection_time.get(track_id, 0)
                        distance_moved = self.calculate_distance(
                            car_center, self.previous_positions.get(track_id, car_center)
                        )

                        # idolimit lejart + kocsi mozgott vagy tul sokaig nem mozgott
                        if time_since_last_detection > self.time_threshold or distance_moved > self.position_threshold:
                            if track_id not in self.detected_vehicles:  # uj kocsi, szamlalo noveles
                                self.detected_vehicles.add(track_id)
                                self.car_count += 1

                            # ido es poz. frissites
                            self.last_detection_time[track_id] = current_time
                            self.previous_positions[track_id] = car_center

                        # tul hosszu ideig all detektalt auto, de meg nincs regisztralva
                        elif time_since_last_detection > self.stationary_threshold:
                            # csak akkor det. ujra ha az auto mozog
                            if track_id in self.detected_vehicles:
                                self.last_detection_time[track_id] = current_time

                        # ID és keret megjelenitese
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f'ID: {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            response["number_of_vehicles_detected"] = len(self.detected_vehicles)

        # szamlalo megjel. arnyekkal
        self.draw_text_with_shadow(
            frame,
            f'Total Vehicles Counted: {self.car_count}',
            (10, 30),  # Pozíció
            font=cv2.FONT_HERSHEY_SIMPLEX,
            font_scale=1.2,
            text_color=(255, 255, 255),  # Fehér szöveg
            shadow_color=(0, 0, 0),  # Fekete árnyék
            thickness=3
        )

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

            # Képkocka autó felismeréshez
            self.process_frame(frame)

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
    tracker = VehicleDetectionTracker(position_threshold=50, time_threshold=10, stationary_threshold=10)
    tracker.process_video(video_path)

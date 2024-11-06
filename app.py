from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/upload', methods=["POST"])
def upload_media():
    """
    Vár egy Arraybuffer api request-et, majd létrehoz számára egy fájlt
    a következő elérési útvonalon: media-file.mp4
    :return: Szöveg arról, hogy sikerült a fájlfeltöltés
    """
    media_file = open("media-file.mp4", "wb")
    media_file.write(request.data)
    media_file.close()

    # Feltöltésre került az mp4 fájl, és az el van tárolva a következő helyen: media-file.mp4
    # TODO: Hívd meg ezen videóra a YOLO algoritmust, és hozz létre egy media-file-result.mp4 videót az eredménynek (amennyiben lehetséges)
    return "Finished"


@app.route('/fetch', methods=["GET"])
def fetch_media():
    # TODO: A yolo algoritmus eredményét olvasd be (ami feltehetően egy mp4) videó és küld vissza azt a frontend-nek.
    return "Finished"


if __name__ == '__main__':
    app.run()

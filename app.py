from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import cv2
from ultralytics import YOLO
import easyocr
from deep_translator import GoogleTranslator
from gtts import gTTS
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load models
yolo_model = YOLO("yolov8n.pt")
ocr_reader = easyocr.Reader(['en'])

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files["image"]
        img_id = str(uuid.uuid4()) + ".jpg"
        img_path = os.path.join(UPLOAD_FOLDER, img_id)
        file.save(img_path)

        img = cv2.imread(img_path)
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # ---------------------------
        # YOLO OBJECT DETECTION
        # ---------------------------
        detected_objects = []

        try:
            results = yolo_model(img_path)
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        label = yolo_model.names.get(cls, "unknown")
                        detected_objects.append(label)
        except Exception as e:
            print("YOLO error:", e)

        # REMOVE DUPLICATES + SORT
        detected_objects = sorted(list(set(detected_objects)))

        # ---------------------------
        # OCR TEXT EXTRACTION
        # ---------------------------
        extracted_text = ""

        try:
            ocr_output = ocr_reader.readtext(img_path)
            for item in ocr_output:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    extracted_text += item[1] + " "
        except Exception as e:
            print("OCR error:", e)

        extracted_text = extracted_text.strip()

        # ---------------------------
        # BUILD FINAL TEXT
        # ---------------------------
        objects_text = ", ".join(detected_objects)

        if extracted_text:
            final_text = f"Detected objects: {objects_text}. Extracted text: {extracted_text}"
        else:
            final_text = f"Detected objects: {objects_text}"

        # ---------------------------
        # TRANSLATION + AUDIO
        # ---------------------------
        langs = {
            "english": "en",
            "hindi": "hi",
            "german": "de",
            "french": "fr",
            "spanish": "es"
        }

        translations = {}
        audio_files = {}

        for lang_name, lang_code in langs.items():
            try:
                translated = GoogleTranslator(source="auto", target=lang_code).translate(final_text)
            except:
                translated = "Translation failed"

            translations[lang_name] = translated

            try:
                audio_filename = f"{uuid.uuid4()}.mp3"
                audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)

                tts = gTTS(translated, lang=lang_code)
                tts.save(audio_path)

                audio_files[lang_name] = audio_filename
            except Exception as e:
                print("TTS error:", e)

        return jsonify({
            "objects": detected_objects,
            "text": extracted_text,
            "translations": translations,
            "audio": audio_files
        })

    except Exception as e:
        return jsonify({"error": "Server crashed", "details": str(e)}), 500

@app.route('/audio/<name>')
def get_audio(name):
    return send_from_directory(OUTPUT_FOLDER, name)

if __name__ == "__main__":
    app.run(debug=True)

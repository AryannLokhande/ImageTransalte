from ultralytics import YOLO
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# Load YOLO model (first time it will download automatically)
model = YOLO("yolov8n.pt")

# Image file name (make sure test.png is in same folder)
image_name = input("Enter image file name: ")
image_path = image_name

# Detect objects
results = model(image_path)
import cv2

annotated_filename = "annotated_" + image_name
annotated_path = os.path.join("uploads", annotated_filename)

for result in results:
    plotted_image = result.plot()  # Draw bounding boxes
    cv2.imwrite(annotated_path, plotted_image)

# Languages to translate
languages = {
    "Hindi": "hi",
    "German": "de",
    "Spanish": "es",
    "French": "fr"
}

# Process results
detected_objects = []

for result in results:
    boxes = result.boxes
    for box in boxes:
        label_index = int(box.cls[0])
        label = model.names[label_index]
        confidence = float(box.conf[0])

        # Filter low confidence detections
        if confidence > 0.5:
            detected_objects.append({
                "object": label,
                "confidence": round(confidence, 2)
            })

        for lang_name, lang_code in languages.items():
            translated = GoogleTranslator(source='auto', target=lang_code).translate(label)
            print(f"{lang_name}: {translated}")

            # Create voice
            tts = gTTS(text=translated, lang=lang_code)
            filename = f"voice_{lang_code}.mp3"
            tts.save(filename)

            # Play voice (Windows)
            os.system(f"start {filename}")
import easyocr
from deep_translator import GoogleTranslator

# STEP 1 — Read text from image
reader = easyocr.Reader(['en'])
result = reader.readtext('test.png')

# Combine detected text
text = " ".join([item[1] for item in result])

print("Detected Text:", text)

# STEP 2 — Translate to Hindi
translated = GoogleTranslator(source='auto', target='hi').translate(text)

print("Translated Text:", translated)
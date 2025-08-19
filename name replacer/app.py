
from flask import Flask, render_template, request, send_file
import os
import datetime
from nickname_replacer import process_file, extract_text_from_pdf
from wechatmethod2 import detect_and_blur_wechat
from PIL import Image
import fitz

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    file = request.files['document']
    if not file:
        return "No file uploaded."

    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    output_blurred_path = os.path.join(OUTPUT_FOLDER, f"blurred_{filename}")
    output_text_path = os.path.join(OUTPUT_FOLDER, f"anonymized_{filename}.txt")

    # Run barcode blur
    try:
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
            detect_and_blur_wechat(filepath, output_blurred_path)
        elif ext == '.pdf':
            # Convert PDF pages to images and blur barcodes
            doc = fitz.open(filepath)
            for i, page in enumerate(doc):
                pix = page.get_pixmap()
                img_path = os.path.join(OUTPUT_FOLDER, f"page_{i}.png")
                pix.save(img_path)
                detect_and_blur_wechat(img_path, img_path)  # in-place blur
    except Exception as e:
        print(f"Error during barcode blurring: {e}")

    # Run name anonymization
    try:
        modified_text, original_name, fake_name = process_file(filepath)
        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write(modified_text)
    except Exception as e:
        return f"Name anonymization failed: {str(e)}"

    return render_template('result.html',
                           original_name=original_name,
                           fake_name=fake_name,
                           text=modified_text,
                           filename=filename,
                           download_filename=os.path.basename(output_text_path),
                           blurred_image=os.path.basename(output_blurred_path) if ext != '.pdf' else None)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(path, as_attachment=True)

@app.route('/show/<filename>')
def show_image(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

import cv2
from pyzbar.pyzbar import decode

def auto_blur_1d_barcode(image_path, output_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image.")
        return

    barcodes = decode(img)
    if not barcodes:
        print("No barcode detected.")
        return

    for barcode in barcodes:
        x, y, w, h = barcode.rect
        roi = img[y:y+h, x:x+w]
        blurred = cv2.GaussianBlur(roi, (51, 51), 0)
        img[y:y+h, x:x+w] = blurred

    cv2.imwrite(output_path, img)
    print(f"✅ Barcode blurred and saved to {output_path}")

# Usage
auto_blur_1d_barcode("img1.jpg", "blurred_img1.jpg")

import cv2
import numpy as np

def detect_and_blur_wechat(input_image, output_image):
    # Load image
    img = cv2.imread(input_image)
    if img is None:
        print("Failed to load image.")
        return

    # Initialize the WeChat QR/barcode detector
    detector = cv2.wechat_qrcode_WeChatQRCode(
        "detect.prototxt", "detect.caffemodel",
        None, None  # sr models optional
    )

    # Detect and decode — returns (decoded_strings, box_points)
    decoded, boxes = detector.detectAndDecode(img)

    if not boxes or boxes is None:
        print("No QR or barcode detected.")
        return

    # boxes is a list (or tuple) of Nx4x2 arrays
    for pts in boxes:
        pts = np.array(pts, dtype=int)
        x, y, w, h = cv2.boundingRect(pts)
        roi = img[y:y+h, x:x+w]
        blurred = cv2.GaussianBlur(roi, (51, 51), 0)
        img[y:y+h, x:x+w] = blurred

    # Save the final image
    cv2.imwrite(output_image, img)
    print(f"✅ Blurred output saved to: {output_image}")

if __name__ == "__main__":
    input_file = "barcode.webp"             # Your input file
    output_file = "output_blurred.png"   # Your desired output file
    detect_and_blur_wechat(input_file, output_file)

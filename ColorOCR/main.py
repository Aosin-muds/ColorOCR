from colorocr import ColorOCR
import cv2

# Load image "sample.jpeg" (ensure it's in the same directory)
image = cv2.imread('sample.jpeg')
if image is None:
    raise FileNotFoundError("Image file 'sample.jpeg' not found.")

# Create an instance of ColorOCR.
# A default target color is required; if not provided, a ValueError is raised.
ocr_instance = ColorOCR(languages=['en'], gpu=False,
                         default_ratio_threshold=0.2, default_target_color='deep_red')

# Add the "deep_red" preset (a darker red)
ocr_instance.add_color_preset(
    "deep_red",
    [
        ([0, 100, 100], [10, 255, 255]),
        ([170, 100, 100], [180, 255, 255])
    ],
    mode="HSV"
)

# Perform OCR in highlight mode using the default settings.
results = ocr_instance.ocr_highlight(image)

# Output text for regions that matched "deep_red"
print("=== Text recognized as deep_red ===")
for res in results:
    if 'deep_red' in res['matched_colors']:
        print(res['text'])

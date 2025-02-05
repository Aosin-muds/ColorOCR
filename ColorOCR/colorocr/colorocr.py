import easyocr
import cv2
import numpy as np
import matplotlib.pyplot as plt

class ColorOCR:
    """
    ColorOCR is a library that uses EasyOCR to perform OCR on image regions
    based on specified colors.

    It supports:
      1. Filtered mode: performing OCR only on regions matching specified colors.
      2. Highlight mode: performing OCR on the entire image and then determining
         whether each text region matches the specified color.

    Additional features:
      - Default color presets include blue, green, yellow, orange, white, and gray.
      - At instantiation, the default color space (default_color_mode), threshold (default_ratio_threshold),
        and target color (default_target_color) must be specified. If not, an error is raised.
      - A visualize_results() method is provided to draw OCR results on the image.
      - If errors occur (e.g. preset not found), error_feedback() outputs clear feedback.
    """
    def __init__(self, languages=['en'], gpu=True, verbose=False,
                 default_ratio_threshold=0.5, default_color_mode='HSV',
                 default_target_color=None):
        # Enforce that a target color must be provided.
        if default_target_color is None:
            raise ValueError("A default target color must be specified. Please set default_target_color.")
        try:
            self.reader = easyocr.Reader(languages, gpu=gpu, verbose=verbose)
        except Exception as e:
            self.error_feedback("Failed to initialize EasyOCR reader.", e)
        self.default_ratio_threshold = default_ratio_threshold
        self.default_color_mode = default_color_mode.upper()
        self.default_target_color = default_target_color.lower()
        
        # Default presets definition
        self.default_presets = {
            'red': {
                'HSV': [
                    (np.array([0, 50, 50]),   np.array([15, 255, 255])),
                    (np.array([165, 50, 50]), np.array([180, 255, 255]))
                ],
                'RGB': [
                    (np.array([150, 0, 0]),   np.array([255, 100, 100]))
                ]
            },
            'black': {
                'HSV': [
                    (np.array([0, 0, 0]), np.array([180, 255, 70]))
                ],
                'RGB': [
                    (np.array([0, 0, 0]), np.array([50, 50, 50]))
                ]
            },
            'blue': {
                'HSV': [
                    (np.array([90, 50, 50]),  np.array([130, 255, 255]))
                ],
                'RGB': [
                    (np.array([0, 0, 150]),   np.array([80, 80, 255]))
                ]
            },
            'green': {
                'HSV': [
                    (np.array([35, 50, 50]),  np.array([85, 255, 255]))
                ],
                'RGB': [
                    (np.array([0, 150, 0]),   np.array([80, 255, 80]))
                ]
            },
            'yellow': {
                'HSV': [
                    (np.array([20, 50, 50]),  np.array([40, 255, 255]))
                ],
                'RGB': [
                    (np.array([150, 150, 0]), np.array([255, 255, 80]))
                ]
            },
            'orange': {
                'HSV': [
                    (np.array([10, 100, 100]), np.array([25, 255, 255]))
                ],
                'RGB': [
                    (np.array([200, 100, 0]),  np.array([255, 180, 50]))
                ]
            },
            'white': {
                'HSV': [
                    (np.array([0, 0, 200]),   np.array([180, 30, 255]))
                ],
                'RGB': [
                    (np.array([200, 200, 200]), np.array([255, 255, 255]))
                ]
            },
            'gray': {
                'HSV': [
                    (np.array([0, 0, 50]),    np.array([180, 50, 200]))
                ],
                'RGB': [
                    (np.array([50, 50, 50]),  np.array([200, 200, 200]))
                ]
            }
        }
        self.user_presets = {}

    # Error feedback: prints error message in English.
    def error_feedback(self, message, exception=None):
        feedback = "[ERROR] " + message
        if exception is not None:
            feedback += " Exception: " + str(exception)
        print(feedback)

    # Preset management
    def add_color_preset(self, name, bounds, mode='HSV'):
        try:
            converted_bounds = []
            for lb, ub in bounds:
                lb_arr = np.array(lb) if not isinstance(lb, np.ndarray) else lb
                ub_arr = np.array(ub) if not isinstance(ub, np.ndarray) else ub
                converted_bounds.append((lb_arr, ub_arr))
            self.user_presets[name.lower()] = { mode.upper(): converted_bounds }
        except Exception as e:
            self.error_feedback(f"Failed to add preset '{name}'.", e)

    def remove_color_preset(self, name):
        try:
            name = name.lower()
            if name in self.user_presets:
                del self.user_presets[name]
        except Exception as e:
            self.error_feedback(f"Failed to remove preset '{name}'.", e)

    def list_color_presets(self):
        presets = {}
        try:
            for name, preset in self.default_presets.items():
                presets[name] = preset
            for name, preset in self.user_presets.items():
                presets[name] = preset
        except Exception as e:
            self.error_feedback("Failed to list presets.", e)
        return presets

    def get_preset_bounds(self, target_color, color_mode='HSV'):
        target = target_color.lower()
        mode = color_mode.upper()
        if target in self.user_presets and mode in self.user_presets[target]:
            return self.user_presets[target][mode]
        if target in self.default_presets and mode in self.default_presets[target]:
            return self.default_presets[target][mode]
        self.error_feedback(f"Preset for color '{target_color}' in {color_mode} mode not found.")
        return None

    # Image processing / OCR functions
    def create_color_mask(self, image, color_mode='HSV', target_color=None, lower_bound=None, upper_bound=None):
        try:
            if color_mode.upper() == 'HSV':
                proc_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            elif color_mode.upper() == 'RGB':
                proc_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                proc_img = image.copy()

            masks = []
            if target_color is not None:
                if isinstance(target_color, list):
                    for col in target_color:
                        bounds = self.get_preset_bounds(col, color_mode)
                        if bounds is None:
                            self.error_feedback(f"Preset not found for color: {col}. Skipping.")
                            continue
                        for lb, ub in bounds:
                            mask = cv2.inRange(proc_img, lb, ub)
                            masks.append(mask)
                else:
                    bounds = self.get_preset_bounds(target_color, color_mode)
                    if bounds is None:
                        self.error_feedback("Preset not found for specified color. Please provide lower_bound and upper_bound.")
                    else:
                        for lb, ub in bounds:
                            mask = cv2.inRange(proc_img, lb, ub)
                            masks.append(mask)
            else:
                # If target_color is not specified, raise an error.
                self.error_feedback("No target color specified. Please specify a target color.")
                return None

            full_mask = masks[0]
            for m in masks[1:]:
                full_mask = cv2.bitwise_or(full_mask, m)
            return full_mask
        except Exception as e:
            self.error_feedback("Failed to create color mask.", e)
            return None

    def preprocess_for_ocr(self, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return gray
        except Exception as e:
            self.error_feedback("Failed to preprocess image for OCR.", e)
            return image

    def ocr_filtered(self, image, color_mode=None, target_color=None, lower_bound=None, upper_bound=None):
        try:
            if color_mode is None:
                color_mode = self.default_color_mode
            if target_color is None:
                self.error_feedback("Target color is required for ocr_filtered().")
                return None, None, None
            mask = self.create_color_mask(image, color_mode, target_color, lower_bound, upper_bound)
            if mask is None:
                return None, None, None
            filtered = cv2.bitwise_and(image, image, mask=mask)
            processed = self.preprocess_for_ocr(filtered)
            results = self.reader.readtext(processed, detail=1, paragraph=False)
            return results, mask, filtered
        except Exception as e:
            self.error_feedback("Failed to perform filtered OCR.", e)
            return None, None, None

    def region_matches_color(self, region, color_mode=None, target_color=None, ratio_threshold=None):
        try:
            if color_mode is None:
                color_mode = self.default_color_mode
            if ratio_threshold is None:
                ratio_threshold = self.default_ratio_threshold
            if region.size == 0:
                return False
            mask = self.create_color_mask(region, color_mode, target_color)
            if mask is None:
                return False
            ratio = cv2.countNonZero(mask) / (region.shape[0] * region.shape[1])
            return ratio >= ratio_threshold
        except Exception as e:
            self.error_feedback("Failed to check region color match.", e)
            return False

    def region_matched_colors(self, region, color_mode=None, target_colors=None, ratio_threshold=None):
        if ratio_threshold is None:
            ratio_threshold = self.default_ratio_threshold
        if color_mode is None:
            color_mode = self.default_color_mode
        matched = []
        if target_colors is None:
            self.error_feedback("Target color(s) must be specified for region_matched_colors().")
            return matched
        if isinstance(target_colors, list):
            for col in target_colors:
                if self.region_matches_color(region, color_mode, target_color=col, ratio_threshold=ratio_threshold):
                    matched.append(col)
        else:
            if self.region_matches_color(region, color_mode, target_color=target_colors, ratio_threshold=ratio_threshold):
                matched.append(target_colors)
        return matched

    def ocr_highlight(self, image, color_mode=None, target_color=None, ratio_threshold=None):
        try:
            if color_mode is None:
                color_mode = self.default_color_mode
            if target_color is None:
                target_color = self.default_target_color
            if ratio_threshold is None:
                ratio_threshold = self.default_ratio_threshold
            results = self.reader.readtext(image, detail=1, paragraph=False)
            output = []
            for bbox, text, conf in results:
                x_coords = [int(point[0]) for point in bbox]
                y_coords = [int(point[1]) for point in bbox]
                x_min = min(x_coords)
                y_min = min(y_coords)
                x_max = max(x_coords)
                y_max = max(y_coords)
                roi = image[y_min:y_max, x_min:x_max]
                matched = self.region_matched_colors(roi, color_mode, target_colors=target_color, ratio_threshold=ratio_threshold)
                output.append({
                    'bbox': (x_min, y_min, x_max - x_min, y_max - y_min),
                    'text': text,
                    'confidence': conf,
                    'matched_colors': matched
                })
            return output
        except Exception as e:
            self.error_feedback("Failed to perform highlight OCR.", e)
            return []

    # Utility: visualize OCR results on the image
    def visualize_results(self, image, results, box_color=(0, 255, 0), text_color=(0, 255, 0), thickness=2, font_scale=0.8):
        try:
            output = image.copy()
            for result in results:
                x, y, w, h = result.get('bbox', (0, 0, 0, 0))
                text = result.get('text', '')
                cv2.rectangle(output, (x, y), (x+w, y+h), box_color, thickness)
                if text.strip() != "":
                    cv2.putText(output, text, (x, max(y-10, 0)),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
            return output
        except Exception as e:
            self.error_feedback("Failed to visualize results.", e)
            return image

    def set_default_ratio_threshold(self, threshold):
        self.default_ratio_threshold = threshold

    def set_default_color_mode(self, color_mode):
        self.default_color_mode = color_mode.upper()

    def set_default_target_color(self, target_color):
        if target_color is None:
            self.error_feedback("Target color cannot be None.")
        else:
            self.default_target_color = target_color.lower()

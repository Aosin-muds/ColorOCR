# ColorOCR

ColorOCR is a Python library that uses [EasyOCR](https://github.com/JaidedAI/EasyOCR) to perform optical character recognition (OCR) on image regions based on specified colors.  
It supports two primary modes:

1. **Filtered Mode:** Perform OCR only on regions matching specified colors.
2. **Highlight Mode:** Perform OCR on the entire image and then determine whether each text region matches the specified color.

Additionally, ColorOCR provides error feedback and visualization utilities to help you debug and present OCR results.

---

## Features

- **Color-based Filtering:**  
  Extract text only from regions matching a specified target color (e.g. `"red"`, `"deep_red"`).

- **Highlight Mode:**  
  Perform OCR on the entire image and then return only the text regions that match the specified target color.

- **Default Presets:**  
  The library comes with default presets for common colors:  
  - **red**  
  - **black**  
  - **blue**  
  - **green**  
  - **yellow**  
  - **orange**  
  - **white**  
  - **gray**  
  Users can add custom presets via the API.

- **Configurable Defaults:**  
  When creating a `ColorOCR` instance, you **must** specify:
  - The default color space (`default_color_mode`), e.g. `"HSV"` or `"RGB"`.
  - The default threshold for color matching (`default_ratio_threshold`).
  - **The default target color (`default_target_color`) is required.**  
    If not provided, a `ValueError` is raised, ensuring OCR always has a defined target color.

- **Error Feedback:**  
  If an error occurs (e.g. a preset is not found or a target color is not specified), the library outputs clear error messages in English via the `error_feedback()` method.

- **Visualization:**  
  The `visualize_results()` method draws bounding boxes and OCR text on the image, which is useful for debugging or presentation.

---

## Installation

### Using pip

Once published on PyPI, install via:

```bash
pip install ColorOCR
```

## API Reference

### Class: `ColorOCR`

#### Constructor

```python
ColorOCR(languages=['en'], gpu=True, verbose=False,
         default_ratio_threshold=0.5, default_color_mode='HSV',
         default_target_color=<target_color>)
```

- **languages**: List of language codes for EasyOCR (default: `['en']`).
- **gpu**: Boolean flag; set to `True` to use GPU if available.
- **verbose**: Enable verbose output from EasyOCR.
- **default_ratio_threshold**: Float, default threshold for color matching (default: `0.5`).
- **default_color_mode**: String, the color space to use (`"HSV"` or `"RGB"`, default: `"HSV"`).
- **default_target_color**: **(Required)** String, the target color (e.g. `"red"`, ).   
  *If not provided, a `ValueError` is raised.*

#### Methods

- **`add_color_preset(name, bounds, mode='HSV')`**  
  Add or update a custom color preset.  
  - **name**: Preset name (e.g. `"my_red"`).  
  - **bounds**: List of tuples of lower and upper bounds (e.g. `[([0, 40, 40], [20, 255, 255])]`).  
  - **mode**: Color space, `"HSV"` or `"RGB"`.

- **`remove_color_preset(name)`**  
  Remove a custom preset by name.

- **`list_color_presets()`**  
  Returns a dictionary of available presets (both default and user-defined).

- **`get_preset_bounds(target_color, color_mode='HSV')`**  
  Retrieves the preset bounds for the given target color and color space.  
  If not found, an error message is output via `error_feedback()`.

- **`create_color_mask(image, color_mode='HSV', target_color, lower_bound=None, upper_bound=None)`**  
  Creates a mask from the image based on the specified target color (or directly specified bounds).  
  **Note:** If no target color is specified, an error is output and `None` is returned.

- **`preprocess_for_ocr(image)`**  
  Converts the input image to grayscale for OCR processing.

- **`ocr_filtered(image, color_mode=None, target_color, lower_bound=None, upper_bound=None)`**  
  Performs OCR on the filtered region (only where the target color is detected).  
  Returns a tuple: `(OCR results, mask, filtered image)`.  
  **Note:** Target color must be specified (or provided via the default).

- **`region_matches_color(region, color_mode=None, target_color, ratio_threshold=None)`**  
  Checks if the given region matches the specified target color above the given threshold.  
  Returns `True` or `False`.

- **`region_matched_colors(region, color_mode=None, target_colors, ratio_threshold=None)`**  
  For a given region, returns a list of target colors that match based on the threshold.

- **`ocr_highlight(image, color_mode=None, target_color, ratio_threshold=None)`**  
  Performs OCR on the entire image and then filters text regions based on whether they match the specified target color.  
  Returns a list of dictionaries, each containing:  
  - `'bbox'`: Bounding box as `(x, y, width, height)`.
  - `'text'`: Recognized text.
  - `'confidence'`: OCR confidence.
  - `'matched_colors'`: List of target colors that match the region.

- **`visualize_results(image, results, box_color=(0, 255, 0), text_color=(0, 255, 0), thickness=2, font_scale=0.8)`**  
  Draws bounding boxes and OCR text on the image using the results from either `ocr_filtered` or `ocr_highlight`.  
  Returns the image with drawn results.

#### Setter Methods

- **`set_default_ratio_threshold(threshold)`**  
  Updates the default ratio threshold for color matching.

- **`set_default_color_mode(color_mode)`**  
  Updates the default color space (e.g., `"HSV"` or `"RGB"`).

- **`set_default_target_color(target_color)`**  
  Updates the default target color.  
  *Note:* This cannot be set to `None`.

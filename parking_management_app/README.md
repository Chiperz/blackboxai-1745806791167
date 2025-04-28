# Parking Management Application

This is a Python Tkinter GUI application for managing a parking lot. It supports vehicle entry and exit, payment calculation based on parking duration, and ticket generation with barcode display.

## Features

- Vehicle entry and exit management
- Payment calculation based on parking duration
- Ticket generation with barcode display
- Clean and user-friendly GUI interface

## Installation

1. Ensure you have Python 3 installed.
2. Install the required dependencies using pip:

```
pip install -r requirements.txt
```

3. For OCR functionality, you need to install Tesseract OCR engine on your system:
   - On Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - On MacOS (with Homebrew): `brew install tesseract`
   - On Windows: Download and install the Tesseract OCR setup from https://github.com/tesseract-ocr/tesseract/releases/latest
     After installation, add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system PATH environment variable.

4. Ensure your camera device is accessible for the application.


## Usage

Run the application with:

```
python parking_management.py
```

The GUI will open, allowing you to manage parking entries and exits.

## Dependencies

- Tkinter (usually included with Python)
- python-barcode
- Pillow (for image handling)

## Notes

- The application generates a ticket with a barcode for each vehicle entry.
- Payment is calculated based on the duration of parking.

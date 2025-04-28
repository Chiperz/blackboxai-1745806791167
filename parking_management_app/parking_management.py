import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageTk
import os
import tempfile
import cv2
import pytesseract

class ParkingManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parking Management System")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.parking_data = {}  # key: vehicle number, value: entry datetime

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Vehicle Entry Frame
        entry_frame = tk.LabelFrame(self.root, text="Vehicle Entry", padx=10, pady=10)
        entry_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(entry_frame, text="Vehicle Number:").grid(row=0, column=0, sticky="w")
        self.vehicle_entry = tk.Entry(entry_frame, width=20)
        self.vehicle_entry.grid(row=0, column=1, padx=5)

        self.entry_button = tk.Button(entry_frame, text="Enter Vehicle", command=self.enter_vehicle)
        self.entry_button.grid(row=0, column=2, padx=5)

        self.camera_button = tk.Button(entry_frame, text="Capture Vehicle Number", command=self.capture_vehicle_number)
        self.camera_button.grid(row=0, column=3, padx=5)

        # Vehicle Exit Frame
        exit_frame = tk.LabelFrame(self.root, text="Vehicle Exit", padx=10, pady=10)
        exit_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(exit_frame, text="Vehicle Number:").grid(row=0, column=0, sticky="w")
        self.vehicle_exit_entry = tk.Entry(exit_frame, width=20)
        self.vehicle_exit_entry.grid(row=0, column=1, padx=5)

        self.exit_button = tk.Button(exit_frame, text="Exit Vehicle", command=self.exit_vehicle)
        self.exit_button.grid(row=0, column=2, padx=5)

        # Ticket Display Frame
        ticket_frame = tk.LabelFrame(self.root, text="Ticket", padx=10, pady=10)
        ticket_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.ticket_text = tk.Text(ticket_frame, height=10, state="disabled")
        self.ticket_text.pack(side="left", fill="both", expand=True)

        self.barcode_label = tk.Label(ticket_frame)
        self.barcode_label.pack(side="right", padx=10)

    def enter_vehicle(self):
        vehicle_num = self.vehicle_entry.get().strip()
        if not vehicle_num:
            messagebox.showwarning("Input Error", "Please enter a vehicle number.")
            return
        if vehicle_num in self.parking_data:
            messagebox.showwarning("Duplicate Entry", "This vehicle is already in the parking lot.")
            return
        entry_time = datetime.now()
        self.parking_data[vehicle_num] = entry_time
        messagebox.showinfo("Entry Recorded", f"Vehicle {vehicle_num} entered at {entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.vehicle_entry.delete(0, tk.END)
        self.generate_ticket(vehicle_num, entry_time)

    def exit_vehicle(self):
        vehicle_num = self.vehicle_exit_entry.get().strip()
        if not vehicle_num:
            messagebox.showwarning("Input Error", "Please enter a vehicle number.")
            return
        if vehicle_num not in self.parking_data:
            messagebox.showwarning("Not Found", "This vehicle is not found in the parking lot.")
            return
        entry_time = self.parking_data.pop(vehicle_num)
        exit_time = datetime.now()
        duration = exit_time - entry_time
        fee = self.calculate_fee(duration)
        messagebox.showinfo("Payment Due", f"Vehicle {vehicle_num} exited.\nDuration: {self.format_duration(duration)}\nFee: Rp {fee:,.0f}")
        self.vehicle_exit_entry.delete(0, tk.END)
        self.clear_ticket()

    def calculate_fee(self, duration):
        # Simple fee calculation: Rp 20000 per hour, minimum Rp 20000
        hours = duration.total_seconds() / 3600
        fee = max(20000, 20000 * hours)
        return fee

    def format_duration(self, duration):
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}h {minutes}m {seconds}s"

    def generate_ticket(self, vehicle_num, entry_time):
        ticket_info = f"Parking Ticket\n\nVehicle Number: {vehicle_num}\nEntry Time: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nPlease keep this ticket for exit."
        self.ticket_text.config(state="normal")
        self.ticket_text.delete(1.0, tk.END)
        self.ticket_text.insert(tk.END, ticket_info)
        self.ticket_text.config(state="disabled")

        # Generate barcode
        barcode_img = self.create_barcode(vehicle_num)
        if barcode_img:
            self.barcode_photo = ImageTk.PhotoImage(barcode_img)
            self.barcode_label.config(image=self.barcode_photo)
        else:
            self.barcode_label.config(image='')

    def create_barcode(self, data):
        try:
            CODE128 = barcode.get_barcode_class('code128')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                code = CODE128(data, writer=ImageWriter())
                filename = code.save(tmp_file.name)
                img = Image.open(filename)
                img = img.resize((200, 80), Image.ANTIALIAS)
                return img
        except Exception as e:
            messagebox.showerror("Barcode Error", f"Failed to generate barcode: {e}")
            return None

    def clear_ticket(self):
        self.ticket_text.config(state="normal")
        self.ticket_text.delete(1.0, tk.END)
        self.ticket_text.config(state="disabled")
        self.barcode_label.config(image='')

    def capture_vehicle_number(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Cannot access the camera.")
            return
        messagebox.showinfo("Camera", "Press 's' to capture the vehicle number, 'q' to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Camera Error", "Failed to capture image.")
                break
            cv2.imshow('Capture Vehicle Number - Press s to capture, q to quit', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                # Save the captured frame to a temporary file
                temp_filename = tempfile.mktemp(suffix='.png')
                cv2.imwrite(temp_filename, frame)
                cap.release()
                cv2.destroyAllWindows()
                # Perform OCR to extract vehicle number
                vehicle_num = self.ocr_vehicle_number(temp_filename)
                os.remove(temp_filename)
                if vehicle_num:
                    self.vehicle_entry.delete(0, tk.END)
                    self.vehicle_entry.insert(0, vehicle_num)
                    messagebox.showinfo("OCR Result", f"Detected Vehicle Number: {vehicle_num}")
                else:
                    messagebox.showwarning("OCR Result", "Could not detect vehicle number. Please try again.")
                return
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def ocr_vehicle_number(self, image_path):
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Optional: apply thresholding or other preprocessing here
            text = pytesseract.image_to_string(gray, config='--psm 7')
            # Clean the text to extract vehicle number (alphanumeric only)
            vehicle_num = ''.join(filter(str.isalnum, text))
            return vehicle_num
        except Exception as e:
            messagebox.showerror("OCR Error", f"Failed to perform OCR: {e}")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingManagementApp(root)
    root.mainloop()

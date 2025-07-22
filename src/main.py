import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
import numpy as np
import os
import datetime
from PIL import Image, ImageTk

DUT_SERIAL_PORT = 'COM3'
CAMERA_SERIAL_PORT = 'COM5'
BAUDRATE = 38400

def get_positions_for_axes(port, axes):
    positions = {}
    try:
        ser = serial.Serial(port, baudrate=BAUDRATE, timeout=0.5)
        for axis in axes:
            try:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                cmd = f'AXI{axis}:POS?\r'
                ser.write(cmd.encode('ascii'))
                time.sleep(0.1)
                resp = ser.readline().decode('ascii').strip()
                if resp:
                    try:
                        positions[axis] = str(int(float(resp)))
                    except ValueError:
                        positions[axis] = resp
                else:
                    positions[axis] = 'NA'
            except Exception:
                positions[axis] = 'NA'
        ser.close()
    except Exception:
        for axis in axes:
            positions[axis] = 'NA'
    return positions

class DualStageScanGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DS102 Multi-Axis Scan & RayCi Image Capture")
        self.geometry("1500x680")
        self.dut_axes = ['X', 'Y', 'Z', 'U', 'V', 'W']
        self.camera_axes = ['X', 'Y']
        self.entries = {}
        self.check_vars = {}

        # Get initial origins
        self.dut_origin = get_positions_for_axes(DUT_SERIAL_PORT, self.dut_axes)
        self.camera_origin = get_positions_for_axes(CAMERA_SERIAL_PORT, self.camera_axes)

        # --- DUT Umbrella Group (smaller) ---
        self.dut_frame = tk.LabelFrame(self, text="DUT (COM3)", font=("Arial", 13, "bold"), bg="#ccc", bd=3, relief="groove")
        self.dut_frame.place(x=20, y=20, width=480, height=240)

        header = ["Axis", "Enable", "Origin", "Start (pulse)", "Stop (pulse)", "Step (count)"]
        for i, label in enumerate(header):
            tk.Label(self.dut_frame, text=label, font=('Arial', 10, 'bold'), bg="#ccc").grid(row=0, column=i, padx=5, pady=2)

        self.entries['DUT'] = {}
        self.check_vars['DUT'] = {}
        for i, axis in enumerate(self.dut_axes):
            tk.Label(self.dut_frame, text=axis, bg="#ccc").grid(row=i+1, column=0)
            self.check_vars['DUT'][axis] = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(self.dut_frame, variable=self.check_vars['DUT'][axis], bg="#ccc")
            cb.grid(row=i+1, column=1)
            self.entries['DUT'][axis] = {}
            # Origin
            val = self.dut_origin[axis]
            ent = tk.Entry(self.dut_frame, width=9, fg="black", readonlybackground="#ccc")
            ent.grid(row=i+1, column=2)
            ent.insert(0, str(val))
            ent.config(state="readonly")
            self.entries['DUT'][axis]['origin'] = ent
            # Start/Stop/Step
            for j, name in enumerate(['start', 'stop', 'step']):
                ent2 = tk.Entry(self.dut_frame, width=9)
                ent2.grid(row=i+1, column=3+j)
                self.entries['DUT'][axis][name] = ent2

        # --- Camera Umbrella Group ---
        self.camera_frame = tk.LabelFrame(self, text="Camera (COM5)", font=("Arial", 13, "bold"), bg="#bbb", bd=3, relief="groove")
        self.camera_frame.place(x=20, y=280, width=350, height=110)

        for i, label in enumerate(header):
            tk.Label(self.camera_frame, text=label, font=('Arial', 10, 'bold'), bg="#bbb").grid(row=0, column=i, padx=5, pady=2)

        self.entries['CAMERA'] = {}
        self.check_vars['CAMERA'] = {}
        for i, axis in enumerate(self.camera_axes):
            tk.Label(self.camera_frame, text=axis, bg="#bbb").grid(row=i+1, column=0)
            self.check_vars['CAMERA'][axis] = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(self.camera_frame, variable=self.check_vars['CAMERA'][axis], bg="#bbb")
            cb.grid(row=i+1, column=1)
            self.entries['CAMERA'][axis] = {}
            val = self.camera_origin[axis]
            ent = tk.Entry(self.camera_frame, width=9, fg="black", readonlybackground="#bbb")
            ent.grid(row=i+1, column=2)
            ent.insert(0, str(val))
            ent.config(state="readonly")
            self.entries['CAMERA'][axis]['origin'] = ent
            for j, name in enumerate(['start', 'stop', 'step']):
                ent2 = tk.Entry(self.camera_frame, width=9)
                ent2.grid(row=i+1, column=3+j)
                self.entries['CAMERA'][axis][name] = ent2

        # --- Global Controls and Image/Progress (from previous code) ---
        self.unitset_btn = tk.Button(self, text="Unit Set", command=self.open_unitset)
        self.unitset_btn.place(x=60, y=550, width=120, height=36)
        self.start_btn = tk.Button(self, text="Start Scan", command=self.start_scan)
        self.start_btn.place(x=220, y=550, width=120, height=36)

        self.progress_label = tk.Label(self, text="", font=('Arial', 12, 'bold'), fg="blue")
        self.progress_label.place(x=370, y=550, width=370, height=36)

        self.image_panel = tk.Label(self, text="Scan image preview here", width=632, height=504, bg="#EEE", anchor='center', relief="sunken")
        self.image_panel.place(x=600, y=20, width=632, height=504)

    def open_unitset(self):
        messagebox.showinfo("Unit Set", "Unit Set dialog logic not yet implemented for dual-stage.")

    def show_scan_image(self, image_path):
        try:
            im = Image.open(image_path)
            photo = ImageTk.PhotoImage(im)
            self.image_panel.configure(image=photo, text="")
            self.image_panel.image = photo
        except Exception as e:
            self.image_panel.configure(text="(Image failed to load)")

    def start_scan(self):
        messagebox.showinfo("Info", "Scan logic for dual stages not yet implemented.")

if __name__ == "__main__":
    app = DualStageScanGUI()
    app.mainloop()

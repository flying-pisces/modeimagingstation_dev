import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
import numpy as np
import os
import datetime
import xmlrpc.client
from PIL import Image, ImageTk

SERIAL_PORT = 'COM3'
BAUDRATE = 38400

def get_all_positions():
    axis_names = ['X', 'Y', 'Z', 'U', 'V', 'W']
    positions = {}
    try:
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=0.5)
        for axis in axis_names:
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
        for axis in axis_names:
            positions[axis] = 'NA'
    return positions

def move_axis_to(ser, axis, pos):
    try:
        cmd = f'AXI{axis}:GOABS {int(round(float(pos)))}\r'
        ser.write(cmd.encode('ascii'))
        # Wait for axis to finish moving
        while True:
            ser.write(f'AXI{axis}:MOTION?\r'.encode('ascii'))
            resp = ser.readline().decode('ascii').strip()
            if resp == '0':
                break
            time.sleep(0.05)
    except Exception as e:
        print(f"Error moving axis {axis}: {e}")

def get_rayci_proxy():
    try:
        server_url = "http://localhost:8080/"
        rayci = xmlrpc.client.ServerProxy(server_url)
        return rayci
    except Exception as e:
        messagebox.showerror("RayCi Error", str(e))
        return None

def capture_bmp(rayci, filename):
    try:
        result = rayci.RayCi.LiveMode.Measurement.newSingle()
        export_result = rayci.RayCi.LiveMode.TwoD.View.exportView(0, filename)
        print(f"Saved image to {filename}")
    except Exception as e:
        print(f"RayCi image capture failed: {e}")

class UnitSetDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Unit Set")
        self.geometry("430x270")
        self.axis_var = tk.StringVar(value=master.axis_names[0])
        self.unit_var = tk.StringVar(value="pulse")
        self.move_val = tk.DoubleVar(value=0)

        tk.Label(self, text="Axis:").grid(row=0, column=0, padx=8, pady=8)
        axis_menu = ttk.Combobox(self, textvariable=self.axis_var, values=master.axis_names, state="readonly")
        axis_menu.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(self, text="Unit:").grid(row=1, column=0, padx=8, pady=8)
        unit_menu = ttk.Combobox(self, textvariable=self.unit_var, values=["pulse", "μm", "deg"], state="readonly")
        unit_menu.grid(row=1, column=1, padx=8, pady=8)

        self.info_label = tk.Label(self, text="1 pulse = 1 (demo)", fg="blue")
        self.info_label.grid(row=2, column=0, columnspan=2, pady=8)
        self.unit_var.trace('w', self.update_conversion_info)
        self.axis_var.trace('w', self.update_conversion_info)

        tk.Label(self, text="Move amount:").grid(row=3, column=0, padx=8, pady=8)
        tk.Entry(self, textvariable=self.move_val, width=12).grid(row=3, column=1, padx=8, pady=8)
        tk.Button(self, text="Run", command=self.run_move).grid(row=4, column=0, columnspan=2, pady=10)

        # Static conversion formula
        formula_text = "Pulse to micron: μm = pulses × [pitch(mm)/steps/rev/microstep] × 1000\n" \
                       "Pulse to degree: ° = pulses × (360/steps/rev/microstep)"
        tk.Label(self, text=formula_text, fg="darkgreen", justify="left",
                 font=("Arial", 9, "italic")).grid(row=5, column=0, columnspan=2, padx=5, pady=12, sticky="w")

    def update_conversion_info(self, *args):
        unit = self.unit_var.get()
        if unit == "pulse":
            self.info_label.config(text="1 pulse = controller step")
        elif unit == "μm":
            self.info_label.config(text="1 pulse = [set by hardware]")
        elif unit == "deg":
            self.info_label.config(text="1 pulse = [set by hardware]")
        else:
            self.info_label.config(text="")

    def run_move(self):
        axis = self.axis_var.get()
        val = self.move_val.get()
        try:
            ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=0.5)
            cmd = f'AXI{axis}:GOABS {int(round(val))}\r'
            ser.write(cmd.encode('ascii'))
            while True:
                ser.write(f'AXI{axis}:MOTION?\r'.encode('ascii'))
                resp = ser.readline().decode('ascii').strip()
                if resp == '0':
                    break
                time.sleep(0.05)
            ser.close()
            messagebox.showinfo("Unit Set", f"Moved {axis} to {val} {self.unit_var.get()}")
        except Exception as e:
            messagebox.showerror("Unit Set Error", str(e))

class ScanGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DS102 Multi-Axis Scan & RayCi Image Capture")
        self.geometry("1300x600")
        self.axis_names = ['X', 'Y', 'Z', 'U', 'V', 'W']
        self.entries = {}
        self.check_vars = {}

        # Query all origins ONCE at startup using robust code
        self.origin_vals = get_all_positions()

        # GUI Header
        header = ["Axis", "Enable", "Origin", "Start (μm)", "Stop (μm)", "Step (count)"]
        for i, label in enumerate(header):
            tk.Label(self, text=label, font=('Arial', 10, 'bold')).grid(row=0, column=i, padx=5, pady=2)

        self.bg = self.cget('bg')
        for i, axis in enumerate(self.axis_names):
            tk.Label(self, text=axis).grid(row=i+1, column=0)
            self.check_vars[axis] = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(self, variable=self.check_vars[axis])
            cb.grid(row=i+1, column=1)
            self.entries[axis] = {}

            val = self.origin_vals[axis]
            ent = tk.Entry(self, width=9, fg="black", readonlybackground=self.bg)
            ent.grid(row=i+1, column=2)
            ent.insert(0, str(val))
            ent.config(state="readonly")
            self.entries[axis]['origin'] = ent

            for j, name in enumerate(['start', 'stop', 'step']):
                ent2 = tk.Entry(self, width=9)
                ent2.grid(row=i+1, column=3+j)
                self.entries[axis][name] = ent2

        self.unitset_btn = tk.Button(self, text="Unit Set", command=self.open_unitset)
        self.unitset_btn.grid(row=len(self.axis_names)+2, column=0, columnspan=2, pady=8)
        self.start_btn = tk.Button(self, text="Start Scan", command=self.start_scan)
        self.start_btn.grid(row=len(self.axis_names)+2, column=2, columnspan=4, pady=8)

        # --- Progress and image display widgets ---
        self.progress_label = tk.Label(self, text="", font=('Arial', 12, 'bold'), fg="blue")
        self.progress_label.grid(row=len(self.axis_names)+3, column=0, columnspan=6, pady=4)

        # Large image preview at true BMP size (632x504)
        self.image_panel = tk.Label(self, text="Scan image preview here", width=632, height=504, bg="#EEE", anchor='center', relief="sunken")
        self.image_panel.place(x=650, y=20, width=632, height=504)

    def open_unitset(self):
        UnitSetDialog(self)

    def show_scan_image(self, image_path):
        try:
            im = Image.open(image_path)
            # Do not resize, show at native size (632x504)
            photo = ImageTk.PhotoImage(im)
            self.image_panel.configure(image=photo, text="")
            self.image_panel.image = photo
        except Exception as e:
            self.image_panel.configure(text="(Image failed to load)")

    def start_scan(self):
        enabled_axes = [ax for ax in self.axis_names if self.check_vars[ax].get()]
        if not enabled_axes:
            messagebox.showwarning("No Axis Selected", "Please enable at least one axis for scanning.")
            return

        # Read scan parameters
        scan_params = {}
        for ax in self.axis_names:
            if self.check_vars[ax].get():
                try:
                    start = float(self.entries[ax]['start'].get())
                    stop = float(self.entries[ax]['stop'].get())
                    step = int(float(self.entries[ax]['step'].get()))
                    if step < 2:
                        messagebox.showerror("Input Error", f"Step (count) for {ax} must be integer ≥2.")
                        return
                    scan_params[ax] = np.linspace(start, stop, step)
                except Exception:
                    messagebox.showerror("Input Error", f"Invalid range/step for {ax}")
                    return
            else:
                # Non-selected axis: fixed at origin
                origin_val = self.origin_vals[ax]
                if origin_val == 'NA':
                    messagebox.showerror("Axis Error", f"Origin value not available for {ax}")
                    return
                scan_params[ax] = np.array([float(origin_val)])

        # Cartesian product of all scan positions
        axes = self.axis_names
        grids = [scan_params[ax] for ax in axes]
        positions = np.array(np.meshgrid(*grids, indexing='ij')).reshape(len(axes), -1).T

        # Prepare log folder
        log_root = os.path.join(os.getcwd(), "log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        log_dir = os.path.join(log_root, timestamp)
        os.makedirs(log_dir, exist_ok=True)

        rayci = get_rayci_proxy()

        try:
            ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=0.5)
            origin_pulses = {ax: float(self.origin_vals[ax]) if self.origin_vals[ax] != 'NA' else 0.0 for ax in axes}
            total = len(positions)

            for idx, pos in enumerate(positions):
                # Move all axes
                for ax, val in zip(axes, pos):
                    move_axis_to(ser, ax, val)
                # Take a picture, build filename
                pos_strs = [f"{ax.lower()}_{int(round(val))}" for ax, val in zip(axes, pos)]
                filename = os.path.join(log_dir, '_'.join(pos_strs) + '.bmp')
                if rayci:
                    capture_bmp(rayci, filename)
                # Show progress and preview
                self.progress_label.config(text=f"Iteration {idx+1} of {total}")
                self.show_scan_image(filename)
                self.update()

            # Return all axes to original positions (BEFORE serial close)
            for ax in axes:
                move_axis_to(ser, ax, origin_pulses[ax])
            ser.close()
            messagebox.showinfo("Scan Completed", "Scan complete and all axes returned to origin.")
        except Exception as e:
            messagebox.showerror("Serial Error", str(e))

if __name__ == "__main__":
    app = ScanGUI()
    app.mainloop()

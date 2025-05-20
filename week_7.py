import tkinter as tk
from tkinter import ttk, messagebox
import serial

class MonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Monitor")
        self.root.geometry("900x550")
        self.root.configure(bg="#F0F4F8")

        self.judul = ["Motor Kanan", "Motor Kiri", "Servo"]
        self.entries = []

        try:
            self.serial_conn = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Tidak bisa membuka port COM3.\n{e}")
            self.serial_conn = None

        tk.Label(self.root, text="SISTEM MONITOR", font=("Segoe UI", 16, "bold"),
                 fg="#0aa1ff", bg="#F0F4F8").pack(pady=15)

        main_frame = tk.Frame(self.root, bg="#F0F4F8")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.left_frame = tk.Frame(main_frame, bg="#F0F4F8")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        self.right_frame = tk.Frame(main_frame, bg="#F0F4F8")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))

        separator = ttk.Separator(main_frame, orient='vertical')
        separator.place(relx=0.5, rely=0, relheight=1)

        self.create_left_side()
        self.create_right_side()
        self.root.after(100, self.read_serial)

    def __del__(self):
        if hasattr(self, 'serial_conn') and self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()

    def update_sensor_value(self, index, value):
        try:
            sensor_value = int(value)
            # Update progress bar
            progress_bar = self.sensor_bars[index]
            progress_bar['value'] = sensor_value
            
            # Change color based on value (threshold can be adjusted)
            if sensor_value > 600:  # Assuming higher value means line detected
                progress_bar.config(style="red.Horizontal.TProgressbar")
            else:
                progress_bar.config(style="green.Horizontal.TProgressbar")
            
            # Update value label
            value_label = getattr(self, f'sensor_value_{index}')
            value_label.config(text=str(sensor_value))
            
        except (ValueError, IndexError):
            pass

    def read_serial(self):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                while self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line.startswith("S1:"):
                        sensor_values = line.split(',')
                        for i, val in enumerate(sensor_values):
                            parts = val.split(':')
                            if len(parts) == 2:
                                self.update_sensor_value(i, parts[1])
            except serial.SerialException:
                pass
        self.root.after(100, self.read_serial)

    def create_left_side(self):
        input_frame = tk.Frame(self.left_frame, bg="#F0F4F8")
        input_frame.pack(fill="x", pady=10)

        for i, label_text in enumerate(self.judul):
            label = tk.Label(input_frame, text=f"{label_text}",
                            font=("Segoe UI", 11, "bold"), fg="#0a75ff", bg="#F0F4F8")
            label.grid(row=i, column=0, sticky="w", pady=6, padx=5)
            
            entry = tk.Entry(input_frame, font=("Segoe UI", 11), width=15, bd=2, relief="groove")
            entry.grid(row=i, column=1, pady=6, padx=5)
            self.entries.append(entry)
            
            btn = tk.Button(input_frame, text="OK", font=("Segoe UI", 9, "bold"),
                            bg="#0a75ff", fg="white", width=4,
                            command=lambda e=entry, l=label_text: self.submit(e, l))
            btn.grid(row=i, column=2, padx=5, pady=6)

        map_nav_frame = tk.Frame(self.left_frame, bg="#FFFFFF", relief="ridge", bd=2)
        map_nav_frame.pack(pady=15, fill="both", expand=True)

        canvas_width = 350
        canvas_height = 160
        self.x_pos, self.y_pos, self.step = canvas_width // 2, canvas_height // 2, 10
        self.direction = "up"

        self.canvas = tk.Canvas(map_nav_frame, width=canvas_width, height=canvas_height, bg="#eef6ff")
        self.canvas.pack(pady=10)

        self.tracker = self.canvas.create_oval(self.x_pos-7, self.y_pos-7,
                                               self.x_pos+7, self.y_pos+7,
                                               fill="#007fff")

        btn_frame = tk.Frame(map_nav_frame, bg="#F0F4F8")
        btn_frame.pack(pady=8)

        btn_opts = {"width": 4, "height": 2, "bg": "#0a75ff", "fg": "white", "font": ("Segoe UI", 12, "bold")}

        tk.Button(btn_frame, text="↑", command=self.move_up, **btn_opts).grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="←", command=self.move_left, **btn_opts).grid(row=1, column=0, padx=8)
        tk.Button(btn_frame, text="↓", command=self.move_down, **btn_opts).grid(row=1, column=1, padx=8)
        tk.Button(btn_frame, text="→", command=self.move_right, **btn_opts).grid(row=1, column=2, padx=8)
        self.status_label = tk.Label(map_nav_frame, text=f"Posisi: ({self.x_pos}, {self.y_pos}) | Arah: {self.direction.upper()}",
                                     font=("Segoe UI", 10, "bold"), bg="#eef6ff", fg="#333333")
        self.status_label.pack(pady=(0, 10))


    def create_right_side(self):
        sensor_frame = tk.Frame(self.right_frame, bg="#F0F4F8")
        sensor_frame.pack(fill="both", expand=True, pady=10)

        tk.Label(sensor_frame, text="Line Sensor Readings", font=("Segoe UI", 14, "bold"),
                fg="#0a75ff", bg="#F0F4F8").pack(pady=10)

        # Create a frame for the sensor bars
        self.sensor_bars_frame = tk.Frame(sensor_frame, bg="#F0F4F8")
        self.sensor_bars_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Configure style for progress bars
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("green.Horizontal.TProgressbar", 
                            troughcolor='#e0e0e0',
                            background='#4CAF50',
                            lightcolor='#4CAF50',
                            darkcolor='#2E7D32')
        self.style.configure("red.Horizontal.TProgressbar", 
                            troughcolor='#e0e0e0',
                            background='#F44336',
                            lightcolor='#F44336',
                            darkcolor='#C62828')

        # Create progress bars for each sensor
        self.sensor_bars = []
        self.sensor_labels = []
        for i in range(5):
            # Label for sensor
            label_frame = tk.Frame(self.sensor_bars_frame, bg="#F0F4F8")
            label_frame.pack(fill="x", pady=2)
            
            label = tk.Label(label_frame, text=f"Sensor {i+1}:", 
                           font=("Segoe UI", 10), bg="#F0F4F8", width=10, anchor="w")
            label.pack(side="left")
            self.sensor_labels.append(label)
            
            # Progress bar
            bar = ttk.Progressbar(label_frame, 
                                orient="horizontal",
                                length=200,
                                mode="determinate",
                                style="green.Horizontal.TProgressbar")
            bar.pack(side="left", padx=5, fill="x", expand=True)
            bar['value'] = 0
            self.sensor_bars.append(bar)
            
            # Value label
            value_label = tk.Label(label_frame, text="0", 
                                 font=("Segoe UI", 10), bg="#F0F4F8", width=5)
            value_label.pack(side="left")
            setattr(self, f'sensor_value_{i}', value_label)

    def move_tracker(self, dx, dy):
        new_x = self.x_pos + dx
        new_y = self.y_pos + dy

        if 0 < new_x < 350 and 0 < new_y < 160:
            self.canvas.move(self.tracker, dx, dy)
            self.x_pos = new_x
            self.y_pos = new_y
            self.update_status_label()

        def update_status_label(self):
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Posisi: ({self.x_pos}, {self.y_pos}) | Arah: {self.direction.upper()}")



    def move_up(self):
        self.direction = "up"
        self.move_tracker(0, -self.step)

    def move_down(self):
        self.direction = "down"
        self.move_tracker(0, self.step)

    def move_left(self):
        self.direction = "left"
        self.move_tracker(-self.step, 0)

    def move_right(self):
        self.direction = "right"
        self.move_tracker(self.step, 0)



    def submit(self, entry, label):
        val = entry.get()
        if val.lstrip('-').isdigit():  # Menerima nilai negatif
            int_val = int(val)
            if 0 <= int_val <= 255:
                messagebox.showinfo("Sukses", f"{label} sebesar: {val}")
                if self.serial_conn and self.serial_conn.is_open:
                    try:
                        if label == "Motor Kanan":
                            self.serial_conn.write(f"R:{val}\n".encode())
                        elif label == "Motor Kiri":
                            self.serial_conn.write(f"L:{val}\n".encode())
                        elif label == "Servo":
                            self.serial_conn.write(f"S:{val}\n".encode())
                    except serial.SerialException:
                        messagebox.showerror("Error", "Gagal mengirim data ke perangkat Serial.")
            else:
                messagebox.showwarning("Error", f"Input {label} harus antara -255 sampai 255.")
        else:
            messagebox.showwarning("Error", f"Input {label} harus angka.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorApp(root)
    root.mainloop()

#terbaru untuk week 6
import serial
import tkinter as tk
from tkinter import ttk, messagebox
import time

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

class MotorControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kontrol Motor DC & Servo ESP8266")
        self.root.geometry("500x400")
        self.root.configure(bg="lightblue")

        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
        except Exception as e:
            messagebox.showerror("Serial Error", f"Gagal membuka port serial:\n{e}")
            self.ser = None

        self.setup_ui()

    def setup_ui(self):
        title = ttk.Label(self.root, text="System Monitor & Tracker", font=("Helvetica", 16, "bold"), background="lightblue", foreground="purple")
        title.pack(pady=10)

        container = ttk.Frame(self.root)
        container.pack(padx=10, pady=10, fill="both", expand=True)

        # Frame Motor
        motor_frame = ttk.LabelFrame(container, text="Motor DC", padding=10)
        motor_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.create_motor_ui(motor_frame)

        # Frame Servo
        servo_frame = ttk.LabelFrame(container, text="Servo Motor", padding=10)
        servo_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.create_servo_ui(servo_frame)

        # Allow resizing
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

    def create_motor_ui(self, frame):
        for i, label in enumerate(["Motor A", "Motor B"]):
            tk.Label(frame, text=label, font=("Arial", 12)).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(frame, width=10)
            entry.grid(row=i, column=1, padx=5)
            ttk.Button(frame, text="Kirim", command=lambda e=entry, m=label: self.send_motor_command(e, m)).grid(row=i, column=2, padx=5)

        ttk.Button(frame, text="STOP Semua Motor", command=self.stop_all_motors).grid(row=2, column=0, columnspan=3, pady=10)

    def create_servo_ui(self, frame):
        tk.Label(frame, text="Sudut Servo (0-180):", font=("Arial", 12)).pack(pady=5)
        self.servo_entry = tk.Entry(frame, width=10)
        self.servo_entry.pack()
        ttk.Button(frame, text="Kirim", command=self.send_servo_command).pack(pady=10)

    def send_motor_command(self, entry, motor):
        if not self.ser or not self.ser.is_open:
            return messagebox.showerror("Serial Error", "Port serial tidak tersedia.")
        try:
            pwm = int(entry.get())
            if not -255 <= pwm <= 255:
                raise ValueError("Rentang PWM -255 hingga 255")
            prefix = "MB" if motor == "Motor B" else "MA"
            command = f"{prefix}:{pwm}\n"
            self.ser.write(command.encode())
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", str(e))

    def send_servo_command(self):
        if not self.ser or not self.ser.is_open:
            return messagebox.showerror("Serial Error", "Port serial tidak tersedia.")
        try:
            angle = int(self.servo_entry.get())
            if not 0 <= angle <= 180:
                raise ValueError("Sudut harus antara 0 dan 180")
            command = f"S:{angle}\n"
            self.ser.write(command.encode())
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", str(e))

    def stop_all_motors(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(b"MA:0\n")
                self.ser.write(b"MB:0\n")
            except serial.SerialException as e:
                messagebox.showerror("Serial Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MotorControlApp(root)
    root.mainloop()

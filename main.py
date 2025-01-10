import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from skimage.color import rgb2gray
from skimage.filters import gaussian
from scipy.ndimage import uniform_filter1d

vehicle_cascade = cv2.CascadeClassifier(r'C:\\Users\\lenovo\\Pictures\\sab kuch\\Code with harry python\\haarcascade_car.xml')

if vehicle_cascade.empty():
    raise IOError("Error: Unable to load the Haar cascade file. Check the file path.")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera is not accessible.")
    exit()

running = False
stop_event = threading.Event() 


def detect_vehicles(frame):
    gray = rgb2gray(frame)
    gray = (gray * 255).astype(np.uint8)
    vehicles = vehicle_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    for (x, y, w, h) in vehicles:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return frame, len(vehicles)

class TrafficGUI:
    def _init_(self, root):
        self.root = root
        self.root.title("Traffic Management System")

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Traffic Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Vehicles")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_monitoring)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.log = tk.Text(self.root, height=10, state=tk.DISABLED)
        self.log.pack()

        self.traffic_data = []
        self.smoothed_data = []
    def update_graph(self, vehicle_count):
        self.traffic_data.append(vehicle_count)

        if len(self.traffic_data) > 5:
            self.smoothed_data = uniform_filter1d(self.traffic_data, size=5)
        else:
            self.smoothed_data = [] 

        self.ax.clear()
        self.ax.plot(self.traffic_data, label="Traffic Count", color="red")

        if len(self.smoothed_data) > 0:
            self.ax.plot(range(len(self.smoothed_data)), self.smoothed_data, label="Smoothed Data", color="green")

        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def add_log(self, message):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
        print(message)

    def start_monitoring(self):
        global running
        if not running:
            running = True
            stop_event.clear()
            self.add_log("Traffic Monitoring is On.")

    def stop_monitoring(self):
        global running
        if running:
            running = False
            stop_event.set()
            self.add_log("Traffic monitoring stopped.")


def traffic_monitor(gui):
    global running
    try:
        while True:
            if not running:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame.")
                break

            processed_frame, vehicle_count = detect_vehicles(frame)
            cv2.putText(processed_frame, f'Vehicles: {vehicle_count}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("Traffic Feed", processed_frame)

            gui.update_graph(vehicle_count)
            gui.add_log(f"Detected {vehicle_count} vehicles.")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                gui.stop_monitoring()
                break

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("Program interrupted by the user.")

    finally:
        cap.release()
        cv2.destroyAllWindows()



root = tk.Tk()
gui = TrafficGUI(root)
traffic_thread = threading.Thread(target=traffic_monitor, args=(gui,), daemon=True)
traffic_thread.start()
root.mainloop()

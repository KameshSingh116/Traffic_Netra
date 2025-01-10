import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from skimage.color import rgb2gray
from scipy.ndimage import uniform_filter1d
import random

# Load Haar Cascade for vehicle detection
vehicle_cascade = cv2.CascadeClassifier(r'C:\Users\lenovo\Pictures\sab kuch\Code with harry python\haarcascade_car.xml')
if vehicle_cascade.empty():
    raise IOError("Error: Unable to load the Haar cascade file. Check the file path.")

# Initialize video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Error: Camera is not accessible.")

running = False
stop_event = threading.Event()

# Vehicle properties
vehicle_types = {
    "car": {"dimension": 1, "speed": 10},
    "bus": {"dimension": 2, "speed": 5},
    "bike": {"dimension": 0.5, "speed": 15},
}

class Vehicle:
    def __init__(self, vehicle_type, dimension, speed):  # Corrected __init__ method
        self.vehicle_type = vehicle_type
        self.dimension = dimension
        self.speed = speed
        self.travel_progress = 0

class RoadSection:
    def __init__(self, name, length, width):  # Corrected __init__ method
        self.name = name
        self.length = length
        self.width = width
        self.vehicles = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def move_vehicles(self):
        passed_vehicles = []
        for vehicle in self.vehicles:
            vehicle.travel_progress += vehicle.speed
            if vehicle.travel_progress >= self.length:
                passed_vehicles.append(vehicle)
        self.vehicles = [v for v in self.vehicles if v not in passed_vehicles]
        return passed_vehicles

class TrafficSignal:
    def __init__(self, signal_id, green_time=30, amber_time=5):  # Corrected __init__ method
        self.signal_id = signal_id
        self.green_time = green_time
        self.amber_time = amber_time
        self.current_light = "green"
        self.time_elapsed = 0
        self.previous_vehicles = 0
        self.congestion_factor = 1

    def update(self, vehicle_count, min_green_time=15, max_green_time=60, congestion_threshold=1.2):
        self.time_elapsed += 1

        if self.current_light == "green" and self.time_elapsed > self.green_time:
            self.current_light = "amber"
            self.time_elapsed = 0

        if self.current_light == "amber" and self.time_elapsed > self.amber_time:
            self.current_light = "red"
            self.time_elapsed = 0
            self.congestion_factor = vehicle_count / (self.previous_vehicles + 1e-6)
            self.previous_vehicles = vehicle_count

        if self.current_light == "red":
            self.current_light = "green"
            self.time_elapsed = 0

        if self.current_light == "green":
            if self.congestion_factor > congestion_threshold:
                self.green_time = min(self.green_time + 5, max_green_time)
            elif self.congestion_factor < 1:
                self.green_time = max(self.green_time - 3, min_green_time)


class TrafficGUI:
    def __init__(self, root):  # Correctly define the constructor with root as an argument
        self.root = root
        self.root.title("Traffic Management System")

        # Matplotlib Figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Traffic Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Vehicles")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Control Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_monitoring)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Log Section
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
        self.ax.set_title("Traffic Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Vehicles")
        self.ax.grid(True)

        self.ax.plot(self.traffic_data, label="Real-Time Traffic", color="red")

        if len(self.smoothed_data) > 0:
            self.ax.plot(range(len(self.smoothed_data)), self.smoothed_data, label="Smoothed Data", color="green")

        self.ax.legend()
        self.canvas.draw()

    def add_log(self, message):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

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
            self.add_log("Traffic Monitoring is Off.")


# Vehicle Detection Function
def detect_vehicles(frame):
    frame = cv2.resize(frame, (640, 480))
    gray = rgb2gray(frame)
    gray = (gray * 255).astype(np.uint8)
    vehicles = vehicle_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    for (x, y, w, h) in vehicles:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return frame, len(vehicles)

# Traffic Monitoring Thread
def traffic_monitor(gui, road, signal):
    global running
    try:
        while not stop_event.is_set():
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

            road.add_vehicle(Vehicle("car", dimension=1, speed=10))
            road.move_vehicles()
            signal.update(vehicle_count)

            gui.update_graph(vehicle_count)
            gui.add_log(f"Detected {vehicle_count} vehicles. Signal Green Time: {signal.green_time}s")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                gui.stop_monitoring()
                break

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("Program interrupted by the user.")

    finally:
        cap.release()
        cv2.destroyAllWindows()

# Main Program
if __name__ == "__main__":
    root = tk.Tk()
    gui = TrafficGUI(root)
    road_a = RoadSection("Road A", length=100, width=4)  # No TypeError now
    signal_a = TrafficSignal(signal_id="Signal A", green_time=20)

    monitoring_thread = threading.Thread(target=traffic_monitor, args=(gui, road_a, signal_a), daemon=True)
    monitoring_thread.start()

    root.mainloop()
    stop_event.set()
    monitoring_thread.join()

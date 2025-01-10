import cv2
import time
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from skimage.color import rgb2gray
from scipy.ndimage import uniform_filter1d

# Predefined static data for vehicle dimensions and road
VEHICLE_DIMENSIONS = {
    "Car": (4.5, 1.8),  # Length, Width in meters
    "Truck": (12.0, 2.5),
    "Bike": (2.0, 0.8)
}
ROAD_WIDTH = 10.0  # Road width in meters
TOTAL_VEHICLES = 300
ALLOWED_PERCENTAGE = 0.8
FIRST_JUNCTION_VEHICLES = int(TOTAL_VEHICLES * ALLOWED_PERCENTAGE)
TIME_TO_NEXT_SIGNAL = 30  # Initial time in seconds

# Function to detect vehicles in a static image
def detect_vehicles_static(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise IOError("Error: Unable to load the image. Check the file path.")

    gray = rgb2gray(image)
    gray = (gray * 255).astype(np.uint8)
    vehicle_cascade = cv2.CascadeClassifier(r'C:\\Users\\lenovo\\Pictures\\sab kuch\\Code with harry python\\haarcascade_car.xml')

    if vehicle_cascade.empty():
        raise IOError("Error: Unable to load the Haar cascade file. Check the file path.")

    vehicles = vehicle_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    for (x, y, w, h) in vehicles:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return image, len(vehicles)

class TrafficGUI:
    def __init__(self, root):
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
        self.time_adjustments = []
        self.vehicle_density = []

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
        self.add_log("Traffic Monitoring is On.")
        self.run_traffic_analysis()

    def stop_monitoring(self):
        self.add_log("Traffic Monitoring is Off.")

    def run_traffic_analysis(self):
        image_path = "traffic_crowd.jpg"  # Path to the static image
        processed_image, vehicle_count = detect_vehicles_static(image_path)
        cv2.imshow("Traffic Analysis", processed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        vehicles_passed = 0
        feedback_sent = False
        signal_time = TIME_TO_NEXT_SIGNAL
        current_density = vehicle_count / ROAD_WIDTH

        self.update_graph(vehicle_count)
        self.add_log(f"Detected {vehicle_count} vehicles. Road width: {ROAD_WIDTH:.2f} meters.")

        vehicles_passed += vehicle_count
        self.vehicle_density.append(current_density)

        if vehicles_passed >= FIRST_JUNCTION_VEHICLES and not feedback_sent:
            self.add_log("80% vehicles passed. Synchronizing with subsequent signals.")
            feedback_sent = True

        if feedback_sent and vehicles_passed < FIRST_JUNCTION_VEHICLES:
            signal_time += 5
            self.time_adjustments.append(signal_time)
            self.add_log(f"Adjusted signal time to {signal_time} seconds to maintain flow consistency.")

        if len(self.vehicle_density) > 1:
            density_variation = abs(self.vehicle_density[-1] - self.vehicle_density[-2])
            self.add_log(f"Vehicle density variation: {density_variation:.2f} vehicles/meter.")

root = tk.Tk()
gui = TrafficGUI(root)
root.mainloop()

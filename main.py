import cv2
import time
import threading
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

vehicle_cascade = cv2.CascadeClassifier(r'C:\\Users\\lenovo\\Pictures\\sab kuch\\Code with harry python\\haarcascade_car.xml')

if vehicle_cascade.empty():
    raise IOError("Error: Unable to load the Haar cascade file. Check the file path.")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera is not accessible.")
    exit()

running = True

def stop_program():
    global running
    running = False
    print("Exiting gracefully...")

def detect_vehicles(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    vehicles = vehicle_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
    for (x, y, w, h) in vehicles:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return frame, len(vehicles)

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

        self.log = tk.Text(self.root, height=10)
        self.log.pack()


        self.traffic_data = []
        self.smoothed_data = []

    def update_graph(self, vehicle_count):
        self.traffic_data.append(vehicle_count)

        window_size = 5
        if len(self.traffic_data) >= window_size:
            smoothed = np.convolve(self.traffic_data, np.ones(window_size)/window_size, mode='valid')
            self.smoothed_data = list(smoothed)

        self.ax.clear()
        self.ax.plot(self.traffic_data, label="Irregular Traffic", color="red")
        if self.smoothed_data:
            self.ax.plot(range(len(self.smoothed_data)), self.smoothed_data, label="Smoothed Traffic", color="green")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def add_log(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        print(message)

def traffic_monitor(gui):
    global running
    try:
        while running:
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
                stop_program()
                break

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("Program interrupted manually.")

    finally:
        cap.release()
        cv2.destroyAllWindows()

root = tk.Tk()
gui = TrafficGUI(root)
traffic_thread = threading.Thread(target=traffic_monitor, args=(gui,))
traffic_thread.start()
root.mainloop()

import cv2
import time
import threading
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

vehicle_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_car.xml')
cap = cv2.VideoCapture(0) 

def detect_vehicles(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    vehicles = vehicle_cascade.detectMultiScale(gray, 1.1, 2)
    for (x, y, w, h) in vehicles:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) 
    return frame, len(vehicles)

if __name__ == "__main__":
    while True:
        ret, frame = cap.read()  
        if not ret:
            break
        processed_frame, vehicle_count = detect_vehicles(frame)
        cv2.putText(processed_frame, f'Vehicles: {vehicle_count}', (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
       
        cv2.imshow("Traffic Feed", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def divide_traffic(vehicle_count, max_section_size=10):
    sections = []
    for i in range(0, vehicle_count, max_section_size):
        sections.append((i + 1, min(i + max_section_size, vehicle_count)))
    return sections

vehicle_count = 25
sections = divide_traffic(vehicle_count)
print("Traffic Sections:", sections)


class TrafficManager:
    def __init__(self, sections, time_limit=10):
        self.sections = sections
        self.time_limit = time_limit  
        self.current_section = 0

    def allow_section_to_pass(self):
        if self.current_section < len(self.sections):
            print(f"Allowing Section {self.current_section + 1} to pass: {self.sections[self.current_section]}")
            time.sleep(self.time_limit) 
            self.current_section += 1
        else:
            print("All sections have passed.")

    def start_traffic_management(self):
        while self.current_section < len(self.sections):
            self.allow_section_to_pass()


sections = [(1, 12), (11, 26), (21, 27)]
traffic_manager = TrafficManager(sections)
traffic_thread = threading.Thread(target=traffic_manager.start_traffic_management)
traffic_thread.start()

class FeedbackManager:
    def __init__(self):
        self.section_times = []

    def record_section_time(self, section, time_taken):
        self.section_times.append((section, time_taken))
        print(f"Section {section}: Time Taken = {time_taken} seconds")

    def adjust_time_limits(self, base_time_limit):
        avg_time = sum(time for _, time in self.section_times) / len(self.section_times)
        adjusted_time = max(base_time_limit, avg_time)
        print(f"Adjusted Time Limit: {adjusted_time} seconds")
        return adjusted_time

feedback_manager = FeedbackManager()
feedback_manager.record_section_time(1, 12)
feedback_manager.record_section_time(2, 8)
adjusted_time = feedback_manager.adjust_time_limits(10)



class TrafficGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Management System")

        # Graph
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Traffic Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Vehicles")
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Log
        self.log = tk.Text(self.root, height=10)
        self.log.pack()

    def update_graph(self, data):
        self.ax.clear()
        self.ax.plot(data)
        self.canvas.draw()

    def add_log(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
import cv2
import time


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
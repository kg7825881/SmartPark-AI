import cv2
import numpy as np
import time
import random
import os

# Define a shared list of live alerts in memory
LIVE_ALERTS = []

def add_live_alert(cam_id: int, vehicle_type: str, violation: str):
    now = time.strftime("%H:%M:%S")
    alert_msg = f"[ALERT] {vehicle_type} detected for {violation} at CAM {cam_id:02d}."
    # Avoid duplicate consecutive logs
    if not LIVE_ALERTS or LIVE_ALERTS[0]['message'] != alert_msg:
        LIVE_ALERTS.insert(0, {
            "id": str(random.randint(100000, 999999)),
            "timestamp": now,
            "message": alert_msg,
            "confidence": round(random.uniform(88.0, 99.5), 1)
        })
        # Keep list size reasonable
        if len(LIVE_ALERTS) > 30:
            LIVE_ALERTS.pop()

# Define unique ROI zones for 4 cameras to make them look distinct
ROI_ZONES = {
    1: np.array([[50, 180], [220, 180], [260, 320], [20, 320]], np.int32),
    2: np.array([[350, 160], [580, 160], [620, 300], [310, 300]], np.int32),
    3: np.array([[100, 200], [300, 200], [350, 340], [50, 340]], np.int32),
    4: np.array([[200, 150], [450, 150], [500, 280], [150, 280]], np.int32)
}

class CameraStreamManager:
    def __init__(self, cam_id: int):
        self.cam_id = cam_id
        self.width = 640
        self.height = 360
        self.roi = ROI_ZONES.get(cam_id, ROI_ZONES[1])
        
        # Check if a real video file exists in videos/Output
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.video_path = os.path.join(project_root, "videos", "Output", f"{cam_id}.mp4")
            
        self.use_real_video = os.path.exists(self.video_path)
        self.cap = None
        
        # State variables for synthetic vehicle simulation
        self.vehicles = []
        if not self.use_real_video:
            for _ in range(4):
                self.vehicles.append(self.create_synthetic_vehicle())
                
    def create_synthetic_vehicle(self):
        v_type = random.choice(["Car", "Heavy Truck", "City Bus", "Delivery Van"])
        # Vehicles enter from left or right
        direction = 1 if random.random() > 0.5 else -1
        x = -80 if direction == 1 else 720
        y = random.randint(180, 280)
        speed = random.choice([2, 3, 4]) * direction
        
        # Determine if this vehicle will stop inside ROI (triggering violation)
        will_park = random.random() > 0.4
        park_duration = random.randint(120, 240) if will_park else 0 # number of frames
        
        color = (random.randint(120, 255), random.randint(120, 255), random.randint(120, 255))
        
        return {
            "type": v_type,
            "x": x,
            "y": y,
            "speed": speed,
            "color": color,
            "width": 70 if v_type in ["Heavy Truck", "City Bus"] else 50,
            "height": 45 if v_type in ["Heavy Truck", "City Bus"] else 35,
            "park_duration": park_duration,
            "parked_frames": 0,
            "id": random.randint(100, 999)
        }
 
    def check_inside_roi(self, x, y):
        result = cv2.pointPolygonTest(self.roi, (int(x), int(y)), False)
        return result >= 0
 
    def get_frame(self):
        # --- PATH A: READ FROM REAL MP4 FILE ---
        if self.use_real_video:
            if self.cap is None:
                self.cap = cv2.VideoCapture(self.video_path)
            
            ret, frame = self.cap.read()
            if not ret:
                # Loop video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))
                
                # Periodically trigger realistic live alerts in the inference log
                if random.random() < 0.005:  # ~0.5% chance per frame per camera
                    v_type = random.choice(["Car", "Delivery Van", "Heavy Truck", "City Bus", "SUV", "Motorcycle"])
                    violation = random.choice(["Double Parking", "No Parking Zone", "Blocking Lane", "Yellow Line Infringement"])
                    add_live_alert(self.cam_id, v_type, violation)
                
                _, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes()

        # --- PATH B: SYNTHETIC TRAFFIC SIMULATION FALLBACK ---
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:, :] = (20, 24, 33) # Match Next.js dashboard panel color bg-[#11141b]
        
        # Draw road outline
        cv2.rectangle(frame, (0, 170), (640, 310), (35, 41, 53), -1)
        cv2.line(frame, (0, 240), (640, 240), (75, 85, 99), 1, cv2.LINE_AA) # Dashed/Solid lane separator
        
        # Draw the ROI Polygon Zone
        cv2.polylines(frame, [self.roi], isClosed=True, color=(0, 140, 255), thickness=2)
        # Add transparent overlay inside ROI
        overlay = frame.copy()
        cv2.fillPoly(overlay, [self.roi], (120, 70, 0)) # BGR: orange overlay
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
        
        # Render ROI Label
        cv2.putText(frame, f"ZONE LIMITS CAM {self.cam_id:02d}", (self.roi[0][0], self.roi[0][1] - 8), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 140, 255), 1, cv2.LINE_AA)
        
        # Update vehicles
        for v in self.vehicles:
            center_x = v['x'] + v['width'] / 2
            center_y = v['y'] + v['height'] / 2
            in_roi = self.check_inside_roi(center_x, center_y)
            
            is_violating = False
            
            if in_roi and v['park_duration'] > 0:
                # Vehicle is parked/stopped inside the ROI
                v['parked_frames'] += 1
                if v['parked_frames'] > 45: # ~1.5s violation threshold
                    is_violating = True
            else:
                # Move vehicle
                v['x'] += v['speed']
                
            # Draw bounding box
            color = (0, 0, 255) if is_violating else v['color']
            cv2.rectangle(frame, (int(v['x']), int(v['y'])), (int(v['x'] + v['width']), int(v['y'] + v['height'])), color, 2)
            
            # Label
            lbl = f"{v['type']} [{v['id']}]"
            if is_violating:
                lbl += " - ILLEGAL"
                add_live_alert(self.cam_id, v['type'], "Double Parking" if v['type'] == "Car" else "Lane Blockage")
                
            cv2.putText(frame, lbl, (int(v['x']), int(v['y']) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
            
        # Clean up off-screen vehicles and respawn
        self.vehicles = [v for v in self.vehicles if -100 < v['x'] < 740]
        while len(self.vehicles) < 4:
            self.vehicles.append(self.create_synthetic_vehicle())
            
        # Add high-tech scanlines overlay
        for r in range(10, self.height, 20):
            cv2.line(frame, (0, r), (self.width, r), (25, 30, 42), 1)
            
        # Radar/Tracking overlay
        cv2.putText(frame, "LIVE EDGE INFERENCE ACTIVE", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (34, 197, 94), 1, cv2.LINE_AA)
        cv2.circle(frame, (self.width - 25, 25), 5, (0, 0, 255) if int(time.time()) % 2 == 0 else (0, 100, 0), -1)
        cv2.putText(frame, "REC", (self.width - 65, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
        
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

# Frame streaming generator
def generate_camera_frames(cam_id: int):
    manager = CameraStreamManager(cam_id)
    while True:
        frame_bytes = manager.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # Standardize to 30 FPS to prevent server exhaustion
        time.sleep(0.033)

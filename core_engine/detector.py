import cv2
import time
from ultralytics import YOLO
import numpy as np

# Load pre-trained YOLOv8 model
model = YOLO("yolov8n.pt") 

# Define ROI polygon coordinates (normalized or exact pixels for your video frame)
# Example: Four corners of a restricted roadside lane
ROI_ZONE = np.array([[100, 400], [400, 400], [500, 700], [50, 700]], np.int32)

# Track vehicle duration inside the ROI: { tracker_id: start_time }
tracked_violations = {}
VIOLATION_THRESHOLD_SEC = 10  # Set low for quick hackathon testing (e.g., 10s instead of 3m)

def is_inside_roi(point, roi_polygon):
    """Checks if the center bottom point of a vehicle is inside the no-parking zone."""
    result = cv2.pointPolygonTest(roi_polygon, (int(point[0]), int(point[1])), False)
    return result >= 0

def process_video_feed(video_source):
    cap = cv2.VideoCapture(video_source)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Draw the ROI Zone on the frame visually (Neon Red/Orange for judges)
        cv2.polylines(frame, [ROI_ZONE], isClosed=True, color=(0, 140, 255), thickness=3)
        
        # Track objects using built-in ByteTrack
        results = model.track(frame, persist=True, tracker="bytetrack.yaml")
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            clss = results[0].boxes.cls.cpu().numpy().astype(int)
            
            for box, track_id, cls in zip(boxes, track_ids, clss):
                # 2 = Car, 7 = Truck, 5 = Bus (COCO dataset classes)
                if cls in [2, 5, 7]: 
                    x1, y1, x2, y2 = box
                    # Calculate center bottom of the vehicle (where its tires touch the asphalt)
                    base_point = ((x1 + x2) / 2, y2)
                    
                    if is_inside_roi(base_point, ROI_ZONE):
                        if track_id not in tracked_violations:
                            tracked_violations[track_id] = time.time()
                        else:
                            elapsed_time = time.time() - tracked_violations[track_id]
                            
                            # Annotate tracking text on screen
                            cv2.putText(frame, f"ID: {track_id} Waiting: {int(elapsed_time)}s", 
                                        (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                            
                            if elapsed_time > VIOLATION_THRESHOLD_SEC:
                                # Trigger violation alert boundary box (Red)
                                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)
                                cv2.putText(frame, "ILLEGAL PARKING", (int(x1), int(y1) - 30), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                                
                                # TODO: Dispatch standard JSON payload to backend API here
                    else:
                        # If the vehicle exits the ROI zone, clear it from active monitoring
                        if track_id in tracked_violations:
                            del tracked_violations[track_id]
                            
        cv2.imshow("SmartPark AI - Live Detection Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

# Run the detection engine on a placeholder or your dataset video path
# process_video_feed("path_to_your_dataset_video.mp4")
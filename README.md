📌 Project Overview

This project presents an AI-based Smart Road Safety System that detects potholes and rear vehicles in real time using computer vision and deep learning. The system provides visual and voice alerts to improve road safety and assist drivers.

We implemented and compared multiple YOLO versions (YOLOv8, YOLOv11, and YOLOv26) to evaluate performance, accuracy, and real-time feasibility.

⸻

🎯 Objectives
	•	Detect potholes on roads using real-time camera input
	•	Detect rear vehicles and estimate distance using bounding box size
	•	Provide visual alerts (bounding boxes, warnings)
	•	Provide voice alerts using browser-based Text-to-Speech
	•	Compare YOLOv8, YOLOv11, and YOLOv26 for performance analysis
	•	Deploy the system using Django web framework

🛠️ Tech Stack
	•	Python 3.9
	•	Django
	•	Ultralytics YOLO
	•	OpenCV
	•	cvzone
	•	HTML, CSS, JavaScript
	•	Browser Text-to-Speech (TTS)
	•	Git & GitHub

🚘 Features

🕳️ Pothole Detection
	•	YOLOv26-based pothole detection
	•	Dynamic danger zone detection
	•	Real-time bounding boxes
	•	Visual + voice alerts

🚗 Rear Vehicle Detection
	•	Vehicle detection (excluding persons)
	•	Lane-based filtering (ignores opposite lane)
	•	Distance estimation using bounding box area
	•	Three alert levels:
	•	SAFE
	•	APPROACHING
	•	DANGER (Too Close)

🔊 Alerts
	•	Visual alerts (bounding boxes + warning text)
	•	Voice alerts via browser (Text-to-Speech)
	•	Alert prioritization to avoid repetition

⸻

📊 Distance Estimation Logic

Distance is approximated using bounding box area:
	•	Larger bounding box → closer vehicle
	•	Smaller bounding box → farther vehicle

This avoids extra hardware (LiDAR/Radar) and works well for real-time systems.
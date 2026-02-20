# NOTE:
# macOS compatible
# Backend: detection + alert state
# Frontend: voice alerts via browser TTS

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from django.conf import settings

from .forms import UserRegisterForm, UpdateProfileForm, UpdateUserForm
from .models import Profile, Detected, DetectedVehicle

import cv2
import cvzone
from ultralytics import YOLO
import os
import threading

# ======================================================
# GLOBAL STATES
# ======================================================
CAMERA_RUNNING = False
camera_lock = threading.Lock()
camera_handle = None

settings.REAR_ALERT = False
settings.POTHOLE_ALERT = False
camera_handle = None
CAMERA_RUNNING = False
camera_lock = threading.Lock()

# ======================================================
# LOAD YOLOv26 MODEL ONCE (CRITICAL)
# ======================================================
BASE_DIR = settings.BASE_DIR

POTHOLE_MODEL_PATH = os.path.join(
    BASE_DIR,
    "APP",
    "models",
    "yolov26n_pothole_best.pt"
)

print("Loading YOLOv26 pothole model from:", POTHOLE_MODEL_PATH)
POTHOLE_MODEL = YOLO(POTHOLE_MODEL_PATH)

REAR_MODEL_PATH = os.path.join(
    BASE_DIR,
    "APP",
    "models",
    "vehicle.pt"  # (keep spelling exactly as file)
)

print("Loading rear vehicle model from:", REAR_MODEL_PATH)
REAR_MODEL = YOLO(REAR_MODEL_PATH)

# ======================================================
# BASIC PAGES
# ======================================================

def Landing_1(request):
    return render(request, '1_Landing.html')


def Register_2(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('Login_3')
    return render(request, '2_Register.html', {'form': form})


def Login_3(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('Home_4')
        messages.error(request, 'Invalid credentials')
    return render(request, '3_Login.html')


@login_required
def Logout(request):
    logout(request)
    return redirect('Login_3')


def Home_4(request):
    return render(request, '4_Home.html')

def Teamates_5(request):
    return render(request, '5_Teamates.html')

def Domain_Result_6(request):
    return render(request, '6_Domain_Result.html')

def Problem_Statement_7(request):
    return render(request, '7_Problem_Statement.html')

def Deploy_8(request):
    return render(request, '8_Deploy.html')

def Deploy_9(request):
    return render(request, '9_Deploy.html')

def Per_Info_8(request):
    return render(request, '8_Per_Info.html')

def Per_Database_10(request):
    return render(
        request,
        '10_Per_Database.html',
        {'models': Detected.objects.all()}
    )

def Per_Database_8(request):
    return render(
        request,
        '8_Per_Database.html',
        {'models': DetectedVehicle.objects.all()}
    )

def profile_list(request):
    return render(
        request,
        'profile_list.html',
        {'profiles': Profile.objects.all()}
    )


@login_required
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    return render(
        request,
        'profile.html',
        {
            'user_form': UpdateUserForm(instance=request.user),
            'profile_form': UpdateProfileForm(instance=request.user.profile)
        }
    )

# ======================================================
# POTHOLE STREAM — YOLOv26 SAFE
# ======================================================

def pothole_stream():
    global camera_handle, CAMERA_RUNNING

    with camera_lock:
        if CAMERA_RUNNING:
            return
        CAMERA_RUNNING = True

    camera_handle = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    DANGER_Y = int(480 * 0.7)

    try:
        while CAMERA_RUNNING:
            ret, frame = camera_handle.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))
            results = POTHOLE_MODEL(frame, verbose=False)

            alert = False

            for r in results:
                if r.boxes is None:
                    continue

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < 0.6:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )

                    cvzone.putTextRect(
                        frame,
                        f"POTHOLE {int(conf * 100)}%",
                        (x1 + 8, max(y1 - 10, 60)),
                        scale=1,
                        thickness=2
                    )

                    if y2 > DANGER_Y:
                        alert = True

            settings.POTHOLE_ALERT = alert

            if alert:
                cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    "ALERT",
                    (50, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                buffer.tobytes() +
                b'\r\n'
            )

    finally:
        settings.POTHOLE_ALERT = False
        with camera_lock:
            CAMERA_RUNNING = False

        if camera_handle:
            camera_handle.release()
            camera_handle = None


@login_required
def pothole_video_feed(request):
    return StreamingHttpResponse(
        pothole_stream(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

# ======================================================
# REAR VEHICLE STREAM (SAFE PLACEHOLDER / WORKING)
# ======================================================

def rear_vehicle_stream():
    global CAMERA_RUNNING

    with camera_lock:
        if CAMERA_RUNNING:
            return
        CAMERA_RUNNING = True

    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    FRAME_WIDTH = 640
    LANE_LEFT = int(FRAME_WIDTH * 0.25)
    LANE_RIGHT = int(FRAME_WIDTH * 0.75)

    ALLOWED_VEHICLES = {"car", "bus", "truck", "motorcycle", "bicycle"}

    last_state = "SAFE"

    try:
        while CAMERA_RUNNING:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))
            results = REAR_MODEL(frame, verbose=False)

            state = "SAFE"

            for r in results:
                if r.boxes is None:
                    continue

                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < 0.4:   # 🔥 relaxed
                        continue

                    cls_id = int(box.cls[0])
                    label = REAR_MODEL.names[cls_id].lower()

                    if label not in ALLOWED_VEHICLES:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w = x2 - x1
                    h = y2 - y1
                    area = w * h

                    # ---- LANE FILTER (SOFT) ----
                    center_x = (x1 + x2) // 2
                    box_width = x2 - x1
                    if center_x < LANE_LEFT or center_x > LANE_RIGHT:
                        continue
                    if box_width < 40:
                        continue

                    # ---- DISTANCE ESTIMATION ----
                    if area > 10000:
                        state = "DANGER"
                        color = (0, 0, 255)
                    elif area > 5000:
                        state = "WARNING"
                        color = (0, 165, 255)
                    else:
                        color = (0, 255, 0)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

                    cvzone.putTextRect(
                        frame,
                        f"{label.upper()} | {state}",
                        (x1 + 5, max(40, y1 - 10)),
                        scale=1,
                        thickness=2
                    )

            # ---- ALERT FLAG ----
            settings.REAR_ALERT = state in ("WARNING", "DANGER")

            # ---- VISUAL ALERT ----
            if state == "DANGER":
                cv2.circle(frame, (30, 30), 12, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    "DANGER! VEHICLE TOO CLOSE",
                    (50, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )
            elif state == "WARNING":
                cv2.circle(frame, (30, 30), 12, (0, 165, 255), -1)
                cv2.putText(
                    frame,
                    "WARNING: VEHICLE APPROACHING",
                    (50, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 165, 255),
                    2
                )

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n"
            )

            last_state = state

    finally:
        cap.release()
        settings.REAR_ALERT = False
        with camera_lock:
            CAMERA_RUNNING = False

@login_required
def rear_video_feed(request):
    return StreamingHttpResponse(
        rear_vehicle_stream(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

# ======================================================
# ALERT STATUS (VOICE)
# ======================================================

@login_required
def alert_status(request):
    return JsonResponse({
        "rear": settings.REAR_ALERT,
        "pothole": settings.POTHOLE_ALERT
    })


@login_required
def stop_camera(request):
    global CAMERA_RUNNING, camera_handle
    with camera_lock:
        CAMERA_RUNNING = False
        if camera_handle:
            camera_handle.release()
            camera_handle = None
    return JsonResponse({"status": "stopped"})

@login_required
def profile_list(request):
    return render(
        request,
        'profile_list.html',
        {'profiles': Profile.objects.all()}
    )


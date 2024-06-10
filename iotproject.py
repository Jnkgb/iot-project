import time
import face_recognition
import cv2
from picamera2 import Picamera2
import numpy as np

import socket



import RPi.GPIO as GPIO
buzzer_pin=18
import time
from mfrc522 import SimpleMFRC522

reader=SimpleMFRC522()

HOST = '0.0.0.0'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

while 1:
    id,text = reader.read()
    print(id)
    time.sleep(0.1)
   # GPIO.cleanup()
    if id == 691585424653:
        break

print("Waiting for a connection...")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr} has been established!")
    data = client_socket.recv(1024).decode()
    print(f"Received: {data}")
    client_socket.send("Hello from server!".encode())
    client_socket.close()
    if data == "success":
        break

# Picamera2 초기화
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (1280, 720)}))
intext="qq"
# 이전 사진의 얼굴 인코딩 저장 변수 초기화
previous_face_encoding = None
tolerance = 0.2  # 허용 오차값 설정 (기본값은 0.6, 낮출수록 정확도 증가)

# 사진 촬영 및 얼굴 비교 함수
def capture_and_compare():
    global previous_face_encoding
    global intext

    # 현재 사진 촬영
    frame = picam2.capture_array()

    # BGR에서 RGB로 변환
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 얼굴 인식
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if face_encodings:
        current_face_encoding = face_encodings[0]

        if previous_face_encoding is not None:
            # 얼굴 비교
            match = face_recognition.compare_faces([previous_face_encoding], current_face_encoding, tolerance=tolerance)
            if match[0]:
                intext="The same person detected."
                print(intext)
                cv2.putText(frame, "Same Person", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            else:
                intext="Different person detected."
                print(intext)
                cv2.putText(frame, "Different Person", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
       
        # 현재 얼굴 인코딩을 이전 얼굴 인코딩으로 업데이트
        previous_face_encoding = current_face_encoding

        # 사진 저장
        filename = time.strftime("%Y%m%d-%H%M%S") + ".jpg"
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
    else:
        intext="No face detected in the image."
        print(intext)
        cv2.putText(frame, "No Face Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    return frame, intext

# Picamera2 시작
picam2.start()
time.sleep(2)  # 카메라 초기화 대기

try:
    while True:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(buzzer_pin,GPIO.OUT)

        # 현재 프레임 캡처
        frame = picam2.capture_array()
       
        # 실시간 프레임 표시
        cv2.imshow('Camera', frame)
   #     print(intext+"@@")
       
        # 'z' 키를 누르면 사진 촬영 및 얼굴 비교
        if  intext=="The same person detected.":
            GPIO.output(buzzer_pin,GPIO.HIGH)
            time.sleep(600)
            GPIO.cleanup()
           
            frame, intext = capture_and_compare()
           
           
        else:
            time.sleep(5)
            frame, intext = capture_and_compare()
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            GPIO.cleanup()
            break
except KeyboardInterrupt:
    print("Exiting...")
finally:
    picam2.close()
    cv2.destroyAllWindows()
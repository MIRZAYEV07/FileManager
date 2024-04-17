import io
from PIL import Image, ImageOps
import cv2
import numpy as np
from starlette.datastructures import UploadFile
import os
import hashlib
from datetime import datetime
from minio import Minio
from sqlalchemy.orm import Session
import requests
import random
import string
import pytz

import socket
import re

uzbekistan_timezone = pytz.timezone('Asia/Tashkent')
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
MINIO_PROTOCOL = os.getenv('MINIO_PROTOCOL')
MINIO_HOST = os.getenv('MINIO_HOST')


async def fit_photo_to_requirements(upload_file: UploadFile):
    # Read the uploaded file into a BytesIO object
    contents = await upload_file.read()
    img_stream = io.BytesIO(contents)
    img = Image.open(img_stream)

    # Convert to JPG if necessary
    if img.format != 'JPEG':
        img = img.convert('RGB')

    # Resize the image while maintaining aspect ratio to fit within the limits
    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

    # Face detection and focusing on a single face
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image_cv = np.array(img)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) > 0:
        x, y, w, h = faces[0]  # Focus on the first detected face
        # Calculate margin to include more area around the face
        margin = int(max(w, h) * 0.2)  # 20% margin around the face
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(img.width, x + w + margin * 2)
        h = min(img.height, y + h + margin * 2)
        face_focus = img.crop((x, y, w, h))
        face_focus.thumbnail((360, 360), Image.Resampling.LANCZOS)
        img = face_focus

    # Convert back to BytesIO object
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr = img_byte_arr.getvalue()

    # Compress the image if it's larger than 1MB
    while len(img_byte_arr) > 1 * 1024 * 1024:
        img_stream = io.BytesIO(img_byte_arr)
        img = Image.open(img_stream)
        img.thumbnail((img.size[0] * 0.9, img.size[1] * 0.9), Image.Resampling.LANCZOS)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr = img_byte_arr.getvalue()

    print("Photo adjusted to requirements")
    return img_byte_arr  # Return the processed image bytes


def generate_md5(s: str) -> str:
    # Create an MD5 hash object
    md5_hash = hashlib.md5()

    # Update the hash object with the bytes of the string, encoding needed to convert string to bytes
    md5_hash.update(s.encode('utf-8'))

    # Return the hexadecimal digest of the hash
    return md5_hash.hexdigest()


def set_resolution(cap, width, height):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


def save_upload_file_minio(frame_data, frame_length, camera_id, minio_client, bucket_name=MINIO_BUCKET_NAME):
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=17))
    file_name = f"{file_name}.jpg"
    object_name = os.path.join(str(camera_id), file_name)
    # check
    minio_client.put_object(bucket_name, object_name, frame_data, frame_length, 'image/jpeg')
    return object_name



class OpenVPNManagementInterface:
    def __init__(self, management_ip, management_port, password=None):
        self.management_ip = management_ip
        self.management_port = management_port
        self.password = password
        self.connection = None

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.management_ip, self.management_port))
        if self.password:
            self.send_command(self.password)

    def send_command(self, command, timeout=5):
        if not self.connection:
            raise Exception("Not connected to management interface")
        self.connection.sendall(f"{command}\r\n".encode())

        response = ""
        try:
            while True:
                data = self.connection.recv(4096).decode()
                response += data
                if 'END' in data:
                    break
        except socket.timeout:
            print("Socket timeout reached, assuming end of response.")
        return response

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_connected_devices_ip(self):
        if not self.connection:
            self.connect()
        response = self.send_command("status 2")
        self.disconnect()

        # Regex to match the CLIENT_LIST lines from the response
        client_list_pattern = re.compile(
            r'CLIENT_LIST,(?P<user_name>[^,]+),(?P<real_address>[^,]+),(?P<virtual_address>[^,]+),'
        )

        devices = []

        for match in client_list_pattern.finditer(response):
            device = {
                'user_name': match.group('user_name'),
                'virtual_address': match.group('virtual_address'),
                'real_address': match.group('real_address').split(':')[0]  # Remove port from real address
            }
            devices.append(device)
        devices.pop(0)

        return devices

import os

from cv2 import VideoCapture, imwrite


def take_photo(i):
    cam = VideoCapture(0) # 0 for default camera
    ret, frame = cam.read()
    if ret:
        imwrite(f"current_photo/scan{i}.png", frame)
        photo_taken = f"current_photo/scan{i}.png"

    else:
        print("Failed to capture image.")

    cam.release()
    return photo_taken



def remove_photo(photo):
    if os.path.exists(photo):
        os.remove(photo)
    else:
        print("Could not find photo.")
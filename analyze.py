


from pathlib import Path

import cv2
import numpy as np

from store import grab_faces

_cascade_path = Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml'
_yunet_model_path = Path(__file__).with_name('face_detection_yunet_2026may.onnx')
_face_detector = None
_face_detector_backend = None


def _get_face_detector(image_size):
    global _face_detector, _face_detector_backend

    if _face_detector is None:
        if hasattr(cv2, 'CascadeClassifier') and _cascade_path.is_file():
            _face_detector = cv2.CascadeClassifier(str(_cascade_path))
            if _face_detector.empty():
                raise RuntimeError(f'Could not load face cascade: {_cascade_path}')
            _face_detector_backend = 'cascade'
        elif hasattr(cv2, 'FaceDetectorYN'):
            if not _yunet_model_path.is_file():
                raise FileNotFoundError(
                    f'YuNet face detector model not found: {_yunet_model_path}. '
                    'Download face_detection_yunet_2026may.onnx from '
                    'https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet '
                    'and save it at that path. OpenCV 5 also requires '
                    'OPENCV_FORCE_DNN_ENGINE=4 for this model.'
                )
            _face_detector = cv2.FaceDetectorYN.create(
                str(_yunet_model_path), '', image_size
            )
            _face_detector_backend = 'yunet'
        else:
            raise RuntimeError('No supported OpenCV face detector is available.')

    if _face_detector_backend == 'yunet':
        _face_detector.setInputSize(image_size)
    return _face_detector


def create_face_print(photo):
    # Read and convert to grayscale
    img = cv2.imread(photo)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    image_size = (img.shape[1], img.shape[0])
    detector = _get_face_detector(image_size)
    if _face_detector_backend == 'yunet':
        _, faces = detector.detect(img)
        if faces is None:
            faces = []
    else:
        faces = detector.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        print("No face detected!")
        return None

    # Take the largest face (handle different detector formats)
    if _face_detector_backend == 'yunet':
        # YuNet returns faces as (x1, y1, x2, y2, confidence) or numpy array
        if isinstance(faces, np.ndarray):
            # faces is a 2D array; pick the one with largest area
            best_idx = np.argmax((faces[:, 2] - faces[:, 0]) * (faces[:, 3] - faces[:, 1]))
            best = faces[best_idx]
            x, y = int(best[0]), int(best[1])
            w, h = int(best[2] - best[0]), int(best[3] - best[1])
        else:
            # List of tuples/arrays
            best = max(faces, key=lambda f: (f[2] - f[0]) * (f[3] - f[1]))
            x, y = int(best[0]), int(best[1])
            w, h = int(best[2] - best[0]), int(best[3] - best[1])
    else:
        # CascadeClassifier returns (x, y, w, h)
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = map(int, (x, y, w, h))
    # Clamp bounding box to image bounds
    h_img, w_img = gray.shape
    x = max(0, x)
    y = max(0, y)
    w = min(w, w_img - x)
    h = min(h, h_img - y)

    if w <= 0 or h <= 0:
        print("Face bounding box out of image bounds!")
        return None

    face_roi = gray[y:y+h, x:x+w]
    face_roi = cv2.resize(face_roi, (150, 150))  # Standardize size

    # Flatten into a feature vector (the "face print")
    face_print = face_roi.flatten()
    return face_print.tolist()  # Convert to list for CSV storage



def validate(face_print):
    stored_faces = grab_faces()
    current_print = np.array(face_print, dtype=np.float64)

    for stored_print in stored_faces:
        stored_print = np.array(stored_print, dtype=np.float64)

        # Normalize both vectors to handle lighting differences
        stored_norm = np.linalg.norm(stored_print)
        current_norm = np.linalg.norm(current_print)

        if stored_norm == 0 or current_norm == 0:
            continue

        stored_normalized = stored_print / stored_norm
        current_normalized = current_print / current_norm

        # Calculate cosine similarity (1.0 = identical, 0.0 = orthogonal)
        similarity = np.dot(current_normalized, stored_normalized)

        # If similarity is above threshold, it's a match
        if similarity > 0.9:
            return True  # Match found - person already in database

    return False  # No match - new person

import datetime
import pickle
import sqlite3

_db = sqlite3.connect("faces.db")
_db.execute("""
    CREATE TABLE IF NOT EXISTS face_prints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        face_data BLOB NOT NULL,
        timestamp TEXT NOT NULL
    )
""")
_db.commit()


def store_face(face_print):
    _db.execute(
        "INSERT INTO face_prints (face_data, timestamp) VALUES (?, ?)",
        (pickle.dumps(face_print), datetime.datetime.now().isoformat())
    )
    _db.commit()


def grab_faces():
    rows = _db.execute("SELECT face_data FROM face_prints").fetchall()
    return [pickle.loads(row[0]) for row in rows]


def clear_old_faces():
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    _db.execute("DELETE FROM face_prints WHERE timestamp < ?", (today,))
    _db.commit()
# take the current photo and move it to stored_photos
# also store photo location and date taken in a csv file
import datetime

def store_face(face_print):
    with open("face_print_list.csv", "a") as file:
        file.write(f"{face_print} | {datetime.datetime.now()}\n")
        return


def grab_faces():
    with open("face_print_list.csv", "r") as file:
        lines = file.readlines()
        return [line.strip() for line in lines if line.strip()]


def clear_old_faces():
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    with open("face_print_list.csv", "r") as file:
        lines = file.readlines()

    kept_lines = []
    for line in lines:
        if not line.strip():
            continue
        try:
            timestamp_str = line.split(" | ")[1].strip()
            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
            if timestamp >= today:
                kept_lines.append(line)
        except (IndexError, ValueError):
            kept_lines.append(line)

    with open("face_print_list.csv", "w") as file:
        file.writelines(kept_lines)
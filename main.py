#facial scans to stop scalpers

from colorama import Fore, init

from analyze import validate, create_face_print
from capture import take_photo, remove_photo
from store import store_face, clear_old_faces

#step 1: take a facial scan / photo
#step 2: check if facial scan matches database
#step 3:
# if facial scan matches database, display Red
# if facial scan does not match database, display Green
#step 4: send facial scan to database
#step 5: repeat steps 1-4
# also add dates along with facial scans (delete photos taken before the current date)


init(autoreset=True)

def main():
    i = 0
    clear_old_faces()
    while True:
        i += 1
        input("press enter to take a facial scan")
        photo = take_photo(i)
        if photo is None:
            continue
        else:
            print(photo + "captured")
            face_print = create_face_print(photo)
            remove_photo(photo)
            if face_print is None:
                print(Fore.RED+"No face detected, skipping")
                continue
            valid = validate(face_print)
            if valid:
                print(Fore.RED+"Person already in database")
                continue
            else:
                print(Fore.GREEN+"Your good to go")
                store_face(face_print)


if __name__ == "__main__":
    main()
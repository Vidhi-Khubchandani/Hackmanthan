from flask import Flask, render_template, request, redirect, session, Response
import mysql.connector
import os
import cv2, time
import face_recognition
import numpy as np



app = Flask(__name__)
app.static_folder = 'static'

app.secret_key = os.urandom(24)

conn = mysql.connector.connect(host="sql6.freesqldatabase.com", user="sql6501028", password="GrwReCaYI4", database="sql6501028")
cursor = conn.cursor()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def registration():
    return render_template('register.html')


@app.route('/service')
def service():
    if 'ID' in session:
        return render_template('service.html')
    else:
        redirect('/login')


@app.route('/login_validation', methods=["GET", "POST"])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute(
        """SELECT * FROM `users` WHERE `Email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['ID'] = users[0][0]
        return redirect('/service')
    else:
        return redirect('/')


@app.route('/add_user', methods=["POST"])
def add_user():
    uid = request.form.get('uid')
    uname = request.form.get('uname')
    uemail = request.form.get('uemail')
    upassword = request.form.get('upassword')

    cursor.execute(
        """INSERT INTO `users`(`ID`,`Police ID`, `Name`,`Email`,`password`) VALUES(NULL,'{}','{}','{}', '{}')""".format(uid, uname, uemail,
                                                                                                                upassword))
    conn.commit()

    cursor.execute("""SELECT * FROM `users` WHERE `Email` LIKE '{}'""".format(uemail))
    myuser = cursor.fetchall()
    session['ID'] = myuser[0][0]
    return redirect('/service')


@app.route('/about')
def about():
    return render_template('aboutus.html')


camera = cv2.VideoCapture(0)

vidhi_image = face_recognition.load_image_file("Vidhi/vidhi.jpg")
vidhi_face_encoding = face_recognition.face_encodings(vidhi_image)[0]

known_face_encodings = [
    vidhi_face_encoding,
]

known_face_names = [
    "Vidhi"
]

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:

                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)


            for (top, right, bottom, left), name in zip(face_locations, face_names):

                top *= 4
                right *= 4
                bottom *= 4
                left *= 4


                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)


                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/Open Webcam')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        check, frames = camera.read()
        if not check:
            break
        else:
            numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)

            for (x, y, w, h) in numberPlates:
                area = w * h
                if area > minArea:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(img, "NumberPlate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    imgRoi = img[y:y + h, x:x + w]
                    cv2.imshow("ROI", imgRoi)
            cv2.imshow("Result", img)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.imwrite("cascade\IMAGES" + str(count) + ".jpg", imgRoi)
                cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, "Scan Saved", (15, 265), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)
                cv2.imshow("Result", img)
                cv2.waitKey(500)
                count += 1

@app.route('/detect_number_plate')
def detect():
    return render_template('base.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/logout')
def logout():
    session.pop('ID')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
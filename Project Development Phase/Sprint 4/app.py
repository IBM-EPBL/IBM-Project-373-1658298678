from flask import Flask, render_template,request,flash,redirect,url_for,session, Response
import sqlite3
import os, sys
import tensorflow as tf
from keras.models import load_model
from skimage.transform import resize
import cv2
import numpy as np
from gtts import gTTS
from playsound import playsound

model = load_model('sld_model.h5')
labels = ['0','1','2','3','4','5','6','7','8','9',
'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','Space','T','U','V','W','X','Y','Z']
user = None

app = Flask(__name__)
app.secret_key="123"

con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,contact integer,mail text)")
con.close()

@app.route('/')
def index():
    return render_template('index.html')

camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def detect(frame):
    img = resize(frame,(256,256,1))
    img = np.expand_dims(img,axis=0)
    if(np.max(img)>1):
        img = img/255.0
    prediction = np.argmax(model.predict(img))
    print('\n\n'+labels[prediction]+'\n\n')

    return labels[prediction]

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
     success, frame = camera.read()
     cv2.imwrite('img.jpg', frame)
     text = detect(frame)
     myobj = gTTS(text=text, lang='en', tld='com', slow=False)
     myobj.save('audio.mp3')
     playsound('audio.mp3', True)
     os.remove('audio.mp3')
     return render_template("signtotext.html", pred=text)


@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where email=? and password=?",(email,password))
        data=cur.fetchone()

        if data:
            session["email"]=data["email"]
            session["password"]=data["password"]
            global user
            user = data["name"]
            return redirect("homepage")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))

@app.route('/homepage',methods=["GET","POST"])
def homepage():
    global user
    return render_template("homepage.html",usr=user)

@app.route('/signtotext',methods=["GET","POST"])
def signtotext():
    return render_template("signtotext.html", pred="No sign detected")

@app.route('/texttosign',methods=["GET","POST"])
def texttosign  ():
    return render_template("texttosign.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            email=request.form['email']
            name=request.form['name']
            password=request.form['password']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into customer(email,name,password)values(?,?,?)",(email,name,password))
            con.commit()
            flash("User created  Successfully","success")
        except:
            flash("Error in Insert Operation","danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    global user
    user = ""
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template,request,flash,redirect,url_for,session
import sqlite3

app = Flask(__name__)
app.secret_key="123"

con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,contact integer,mail text)")
con.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        name=request.form['email']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where email=? and password=?",(name,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["name"]
            session["password"]=data["password"]
            return redirect("homepage")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))


@app.route('/homepage',methods=["GET","POST"])
def homepage():
    return render_template("homepage.html")

@app.route('/signtotext',methods=["GET","POST"])
def signtotext():
    return render_template("signtotext.html")

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
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)

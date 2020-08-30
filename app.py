from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import TextField,TextAreaField, SubmitField, validators, ValidationError
from datetime import datetime, timedelta
from pytz import timezone


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///docs.db"
app.secret_key="mysecretkey"
db=SQLAlchemy(app)

class doc_form(Form):
	content=TextAreaField("Entry:",[validators.InputRequired()])
	submit=SubmitField("Submit")


class login_form(Form):
	username=TextField("Enter Name:",[validators.InputRequired()])
	submit=SubmitField("Login")

class Doc(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(40),nullable=False)
	content=db.Column(db.String(500), nullable=False)
	date_time=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		doc=f"{self.username}@({self.date_time.strftime('%m-%d-%Y %H:%M')}):\nEntry:{self.content}"
		return doc

@app.route('/',methods=["POST","GET"])
def login():
	if request.method=="POST":
		if len(request.form['username'])>0:
			session['username']=request.form['username']
			return redirect(url_for('docs'))
	form=login_form()
	return render_template("login.html",form=form)


@app.route('/make/', methods=['GET','POST'])
def docs():
	if "username" in session:
		doc_f=doc_form()	
		return render_template("main.html",form=doc_f)
	else:
		return "Access Denied"

@app.route('/fetch')
def fetch():
	if "username" in session:
		if "From" in request.args and "Till" in request.args and (len(request.args.get('From'))>0 and len(request.args.get('Till'))>0):
			frm=list(map(int,request.args.get('From').split('-')))
			til=list(map(int,request.args.get('Till').split('-')))
			frm=datetime(frm[0],frm[1],frm[2])
			til=datetime(til[0],til[1],til[2])+timedelta(days=1)
			entries=db.session.query(Doc).filter(Doc.date_time>=frm, Doc.date_time<=til).order_by(Doc.date_time.desc()).all()
		else:
			entries=db.session.query(Doc).filter(Doc.date_time>=(datetime.utcnow()-timedelta(days=1))).order_by(Doc.date_time.desc()).all()
		return render_template("fetch.html",entries=entries)
	else:
		return "Access Denied"

@app.route('/show/')
def show():
	if "username" in session:
		return render_template('show.html')
	else:
		return "Access Denied"

@app.route('/demo',methods=["POST","GET"])
def demo():
	if "username" in session:
		if request.method=="POST":
			doc1=Doc(username=session['username'],content=request.form['content'])
			db.session.add(doc1)
			db.session.commit()
			return redirect(url_for("demo"))
		entries=db.session.query(Doc).order_by(Doc.date_time.desc()).limit(3).all()
		return render_template("fetch.html",entries=entries)
	else:
		return "Access Denied"

@app.route('/update',methods=["POST","GET"])
def update():
	if "username" in session:
		if request.method=="POST":

			if ("ID" in request.form) and (str(request.form["ID"]).isdigit()):
				id_e=int(request.form['ID'])
				content_p=str(request.form['content'])
				row=db.session.query(Doc).get(id_e)
				if row!=None:
					row.content=content_p
					db.session.commit()
			return redirect(url_for("update"))
		entries=db.session.query(Doc).order_by(Doc.date_time.desc()).limit(3).all()
		return render_template("fetch.html",entries=entries)
	else:
		return "Access Denied"


@app.route('/logout/')
def logout():
	if "username" in session:
		session.pop("username",None)
		return redirect(url_for('login'))
	else:
		return "Access Denied"

if __name__=="__main__":
	app.run(debug=True,port=9000)
from flask import Flask ,request,Response,session,jsonify,render_template,redirect,url_for
from flask.json import JSONDecoder
from google.protobuf import message
from keras.utils.generic_utils import default
from db import create_db,db
from models import imgModel,User
from flask_restful import marshal_with,fields,abort
import os
from werkzeug.utils import redirect, secure_filename
from keras.models import load_model
from keras.preprocessing import image
import keras 
import numpy as np
import pandas as pd
from flask_cors import CORS,cross_origin
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime
from sqlalchemy import desc
import matplotlib.pyplot as plt
import seaborn as sns
from pyrebase import pyrebase
import pathlib
import urllib.request
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/mobile/*": {"origins": '*'}})

UPLOAD_FOLDER=os.path.join('static','images')
app.config['CORS HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///imgDb.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY']="gyankoissah"

firebaseConfig = {
  "apiKey": "AIzaSyDbZhN0J_vIeursbhHDLC0Byze4-CM_WR4",
  "authDomain": "dronetry-cbc09.firebaseapp.com",
  "databaseURL": "https://dronetry-cbc09-default-rtdb.firebaseio.com",
  "projectId": "dronetry-cbc09",
  "storageBucket": "dronetry-cbc09.appspot.com",
  "messagingSenderId": "475234377420",
  "appId": "1:475234377420:web:de636bed729d33c4ccac69",
  "measurementId": "G-EGHW1E7PFH",
  "serviceAccount": "service.json"
};

firebase=pyrebase.initialize_app(firebaseConfig)
database=firebase.database()
storage=firebase.storage()



create_db(app)

resource_fields ={
    "id":fields.Integer,
    "name":fields.String,
    "mimetype":fields.String,
    "img":fields.String

}


coffeModel =keras.models.load_model("files/CoffeModel.h5")
cottonModel =keras.models.load_model("files/CottonModel.h5")
cocoaModel = keras.models.load_model("files/CocoaModel.h5")


def getPrediction(plant,filename):
    test_image = keras.preprocessing.image.load_img("static/images/"+filename,target_size=(256,256,3))
    test_image = keras.preprocessing.image.img_to_array(test_image)
    test_image = np.expand_dims(test_image,axis=0)
    if plant == "coffe":
        prediction = coffeModel.predict(test_image)
        return prediction
    elif plant == "cotton":
        prediction = cottonModel.predict(test_image)
        return prediction
    elif plant =="cocoa":
        prediction = cocoaModel.predict(test_image)
        return prediction
def getUserPosts(id):
    posts=imgModel.query.filter(imgModel.user==id).order_by(desc(imgModel.id))
    
    data=[]
    for image in posts:
        data.append({'id':str(image.id),'image':image.name,'prediction':image.prediction,"crop":image.crop})
    print(len(data))
    return data

def dataToDataframe(plant):
    user_id=session['user_info']['id']
    posts=imgModel.query.filter((imgModel.user==user_id) & (imgModel.crop==plant))
    predictions=[]
    for data in posts:
        predictions.append(data.prediction)
    if len(predictions) == 0:
        return "No file"
    else:
        if plant =='cotton':
            if os.path.exists("static/graphs/{}cotton.png".format(user_id)):
                os.remove("static/graphs/{}cotton.png".format(user_id))
                picture=sns.countplot(x=predictions)
                plt.title("cotton")
                plt.xticks(rotation=25)
                plt.savefig("static/graphs/{}cotton.png".format(user_id))
                return "file"
            else:
                picture=sns.countplot(x=predictions)
                plt.title("cotton")
                plt.xticks(rotation=25)
                plt.savefig("static/graphs/{}cotton.png".format(user_id))
                return "file"

        elif plant == 'coffe':
            if os.path.exists("static/graphs/{}coffe.png".format(user_id)):
                os.remove("static/graphs/{}coffe.png".format(user_id))
                picture=sns.countplot(x=predictions)
                plt.title("coffe")
                plt.xticks(rotation=25)
                plt.savefig("static/graphs/{}coffe.png".format(user_id))
                return "file"
            else:
                picture=sns.countplot(x=predictions)
                plt.title("coffe")
                plt.xticks(rotation=25)
                plt.savefig("static/graphs/{}coffe.png".format(user_id))
                return "file"
        elif plant=='cocoa':
            if os.path.exists("static/graphs/{}cocoa.png".format(user_id)):
                os.remove("static/graphs/{}cocoa.png".format(user_id))
                picture=sns.countplot(x=predictions)
                plt.xticks(rotation=25)
                plt.title("cocoa")
                plt.savefig("static/graphs/{}cocoa.png".format(user_id))
                return "file"
            else:
                picture=sns.countplot(x=predictions)
                plt.title("cocoa")
                plt.xticks(rotation=25)
                plt.savefig("static/graphs/{}cocoa.png".format(user_id))
                return "file"




@app.route("/home",methods=['GET','POST'])
def home():
    if request.method == 'POST':
        mail=request.form.get('email')
        passw=request.form.get('password')
        user = User.query.filter((User.email==mail) & (User.password==passw)).first()
        if user:
            session['user_info']={'id':user.id,'username':user.fullname,'contact':user.contact,'town':user.town}
            data=getUserPosts(user.id)
            return render_template('index.html',user_data=session['user_info'],posts=data)
        else:
            return render_template("login.html")
    else:
        if 'user_info' in session:
            id=session['user_info']['id']
            data=getUserPosts(id)
            return render_template('index.html',user_data=session['user_info'],posts=data)
        else:
             return render_template('login.html')

@app.route("/figure/<int:num>")
def getFigure(num):
    user_id=session['user_info']['id']
    if num==1:
        file=dataToDataframe("cocoa")
        if file == "file":
            return render_template("figure.html",crop='cocoa',user_data=session['user_info'],path="static/graphs/{}cocoa.png".format(user_id))
        else:
            return render_template("figure.html",crop='no crop',user_data=session['user_info'])
    elif num==2:
        file=dataToDataframe("cotton")
        if file =='file':
            return render_template("figure.html",crop='cotton',user_data=session['user_info'],path="static/graphs/{}cotton.png".format(user_id))
        else:
            return render_template("figure.html",crop='no crop',user_data=session['user_info'])
    elif num == 3:
        file=dataToDataframe("coffe")
        if file =='file':
            return render_template("figure.html",crop='coffe',user_data=session['user_info'],path="static/graphs/{}coffe.png".format(user_id))
        else:
            return render_template("figure.html",crop='no crop',user_data=session['user_info'])
    else:
        return("index.html")


@app.route("/web/login",methods=['GET','POST'])
def Login():
    return render_template("login.html")
    

@app.route("/web/register",methods=['GET','POST'])
def webRegister():
    if request.method =='POST':
        username=request.form.get("username")
        phone=request.form.get("contact")
        city = request.form.get('town')
        mail = request.form.get('email')
        passw = request.form.get('password')
        new_user=User(email=mail,password=passw,fullname=username,contact=phone,town=city)
        db.session.add(new_user)
        db.session.commit()
        return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/crop/<int:num>",methods=['GET'])
def handleCrop(num):
    if 'user_info' in session:
        if num == 1:
            return render_template('upload.html',crop='cocoa',user_data=session['user_info'])
        elif num == 2:
            return render_template('upload.html',crop='cotton',user_data=session['user_info'])
        elif num == 3:
            return render_template('upload.html',crop='coffe',user_data=session['user_info'])
    else:
        return "sorry"

@app.route("/upload",methods=['POST'])
def upload():
    if request.method=="POST":
        picture = request.files['photo']
        plant = str(request.form['crop'])
        if plant == "cotton":
            classes=["diseased cotton leaf","diseased cotton plant","fresh cotton leaf","fresh cotton plant"]
        elif plant == "coffe":
            classes=["cercospora","healthy","miner","phoma","rust"]
        elif plant=="cocoa":
            classes=["blackpod ","frosty pod rot","healthy"]
        if not  picture:
            return {"results":"No is file"}
        filename=secure_filename(picture.filename)
        picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        fullname=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        prediction = getPrediction(plant,filename)
        pred= classes[prediction[0].argmax()]
        user_id=session['user_info']['id']
        img=imgModel(img=picture.read(),name=filename,mimetype=picture.mimetype,crop=plant,user=int(user_id),prediction=pred)
        db.session.add(img)
        db.session.commit()
        return {"status":pred}
    else:
        return render_template("home.html")


@app.route("/droneimages",methods=['GET'])
def handleDroneImages():
    images=[]
    files = storage.list_files()
    for file in files:
        url=storage.child(file.name).get_url(None)
        images.append(url)
    if len(images)==0:
        image=''
    else:
        image=images[-1]
    user_id=session['user_info']['id']
    return  render_template("droneimages.html",user_data=session['user_info'],link=image,id=user_id)



@app.route("/logout",methods=['GET'])
def logout():
    if 'user_info' in session:
        session.pop("user_info",default=None)
        return redirect(url_for('Login'))
    else:
        return redirect(url_for('Login'))


@app.route("/mobile/upload",methods=['POST','GET'])
@cross_origin()
def uploadMobile():
    if request.method=="POST":
        data = request.get_json(force=True)
        picture=data['imageUrl']
        plant=data['crop']
        starter = picture.find(',')
        image_data = picture[starter+1:]
        image_data = bytes(image_data, encoding="ascii")
        picture = Image.open(BytesIO(base64.b64decode(image_data)))
        now=datetime.now()
        date_time = now.strftime("%m%d%Y%H%M%S")
        filename=str(date_time)+"image.jpg"
        picture.save('static/images/'+filename)
        if plant == "cotton":
            classes=["diseased cotton leaf","diseased cotton plant","fresh cotton leaf","fresh cotton plant"]
        elif plant == "coffe":
            classes=["cercospora","healthy","miner","phoma","rust"]
        elif plant=="cocoa":
            classes=["blackpod","frosty pod rot","healthy"]
        if not  picture:
            return {"results":"No is file"}
        prediction = getPrediction(plant,filename)
        pred= classes[prediction[0].argmax()]
        img=imgModel(img=image_data,name=filename,mimetype='jpg',crop=plant,user=int(data['user_id']),prediction=pred)
        db.session.add(img)
        db.session.commit()
        data={"status":pred}
        return jsonify(data),200
    
    if request.method=="GET":
        data = request.get_json(force=True)
        picture=data['imageUrl']
        plant=data['crop']
        starter = picture.find(',')
        image_data = picture[starter+1:]
        image_data = bytes(image_data, encoding="ascii")
        picture = Image.open(BytesIO(base64.b64decode(image_data)))
        now=datetime.now()
        date_time = now.strftime("%m%d%Y%H%M%S")
        filename=str(date_time)+"image.jpg"
        picture.save('static/images/'+filename)
        if plant == "cotton":
            classes=["diseased cotton leaf","diseased cotton plant","fresh cotton leaf","fresh cotton plant"]
        elif plant == "coffe":
            classes=["cercospora","healthy","miner","phoma","rust"]
        elif plant=="cocoa":
            classes=["blackpod","frosty pod rot","healthy"]
        if not  picture:
            return {"results":"No is file"}
        prediction = getPrediction(plant,filename)
        pred= classes[prediction[0].argmax()]
        img=imgModel(img=image_data,name=filename,mimetype='jpg',crop=plant,user=int(session['user_info']['id']),prediction=pred)
        db.session.add(img)
        db.session.commit()
        data={"status":pred}
        return jsonify(data),200


@app.route("/mobile/droneImage",methods=['POST'])
@cross_origin()
def handleDroneImageCapture():
    if request.method=='POST':
        data = request.get_json(force=True)
        plant=data['crop']
        now=datetime.now()
        date_time = now.strftime("%m%d%Y%H%M%S")
        filename=str(date_time)+"image.jpg"
        urllib.request.urlretrieve(data['imageUrl'],'static/images/'+filename)
        picture=Image.open('static/images/'+filename)
        if plant == "cotton":
            classes=["diseased cotton leaf","diseased cotton plant","fresh cotton leaf","fresh cotton plant"]
        elif plant == "coffe":
            classes=["cercospora","healthy","miner","phoma","rust"]
        elif plant=="cocoa":
            classes=["blackpod","frosty pod rot","healthy"]
        if not  picture:
            return {"results":"No is file"}
        prediction = getPrediction(plant,filename)
        pred= classes[prediction[0].argmax()]
        img=imgModel(img=filename,name=filename,mimetype='jpg',crop=plant,user=int(data['user_id']),prediction=pred)
        db.session.add(img)
        db.session.commit()
        data={"status":pred}
        return jsonify(data),200

    

        


@app.route('/mobile/create-user-mobile',methods=['POST'])
@cross_origin()
def createUser():
    if request.method == "POST":
        data = request.get_json(force=True)
        user = User.query.filter_by(email=data['email']).first()
        if user:
             return {"error":"User already exist"}
        new_user=User(email=data['email'],password=data['password'],fullname=data['fullName'],contact=data['contact'],town=data['town'])
        db.session.add(new_user)
        db.session.commit()
        return {'id':new_user.id,'email':new_user.email,'password':new_user.password}


@app.route('/mobile/user-mobile-login',methods=['POST'])
@cross_origin()
def logUserIn():
    if request.method=="POST":
        data=request.get_json(force=True)
        user = User.query.filter((User.email==data['email']) & (User.password==data['password'])).first()
        if user :
            return {'id':user.id,'email':user.email}
        else:
            return {"error":"user not found"}    

@app.route("/mobile/get-user-posts/<int:id>",methods=['GET'])
@cross_origin()
def getUserImages(id):
    posts=imgModel.query.filter_by(user=id).order_by(desc(imgModel.id))
    data=[]
    for image in posts:
        data.append({'id':str(image.id),'image':image.name,'prediction':image.prediction,"crop":image.crop})
    return {'data':data}
@app.route("/mobile/get-user-graph",methods=['GET','POST'])
@cross_origin()
def getUsergraphMobile():
    if request.method =='POST':
        data=request.get_json(force=True)
        plant=str(data['plant'])
        id=int(data['user_id'])
        posts=imgModel.query.filter((imgModel.user==id) & (imgModel.crop==plant))
        predictions=[]
        for data in posts:
            predictions.append(data.prediction)
        if len(predictions) == 0:
            return {'path':'no file'}
        else:
            if plant =='cotton':
                if os.path.exists("static/graphs/{}cotton.png".format(id)):
                    os.remove("static/graphs/{}cotton.png".format(id))
                    picture=sns.countplot(x=predictions)
                    plt.title("cotton")
                    plt.xticks(rotation=20, ha='right')
                    plt.savefig("static/graphs/{}cotton.png".format(id))
                    return {'path':'static/graphs/{}cotton.png'.format(id)}
                else:
                    picture=sns.countplot(x=predictions)
                    plt.title("cotton")
                    plt.xticks(rotation=20, ha='right')
                    plt.savefig("static/graphs/{}cotton.png".format(id))
                    return {'path':'static/graphs/{}cotton.png'.format(id)}
            elif plant == 'coffe':
                if os.path.exists("static/graphs/{}coffe.png".format(id)):
                    os.remove("static/graphs/{}coffe.png".format(id))
                    picture=sns.countplot(x=predictions)
                    plt.title("coffe")
                    plt.savefig("static/graphs/{}coffe.png".format(id))
                    return {'path':'static/graphs/{}coffe.png'.format(id)}
                else:
                    picture=sns.countplot(x=predictions)
                    plt.title("coffe")
                    plt.savefig("static/graphs/{}coffe.png".format(id))
                    return {'path':'static/graphs/{}coffe.png'.format(id)}
            elif plant=="cocoa":
                if os.path.exists("static/graphs/{}cocoa.png".format(id)):
                    os.remove("static/graphs/{}cocoa.png".format(id))
                    picture=sns.countplot(x=predictions)
                    plt.title("coffe")
                    plt.savefig("static/graphs/{}cocoa.png".format(id))
                    return {'path':'static/graphs/{}cocoa.png'.format(id)}
                else:
                    picture=sns.countplot(x=predictions)
                    plt.title("coffe")
                    plt.savefig("static/graphs/{}cocoa.png".format(id))
                    return {'path':'static/graphs/{}cocoa.png'.format(id)}
                

if __name__ == "__main__":
    app.run(debug=True)

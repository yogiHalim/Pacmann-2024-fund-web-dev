from flask import Flask, render_template, Blueprint, redirect, request, jsonify
from flask_cors import CORS
import os
#import datetime
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
#from sqlalchemy import Column, ForeignKey

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt
from sqlalchemy.exc import IntegrityError

vDB=SQLAlchemy()
vMigrate=Migrate()
vJWT=JWTManager()

basedir=os.path.abspath(os.path.dirname(__file__))
DB_URI='sqlite:///'+os.path.join(basedir,'exercise3.db')
class cConfig:
    SECRET_KEY='secret-key-20240320'
    SQLALCHEMY_DATABASE_URI = DB_URI 
    SQLALCHEMY_TRACK_MODIFICATION = False


template_dir2 = os.getcwd()
#template_dir=vApp.root_path
vApp = Flask(__name__, template_folder=template_dir2+'/app')
#def create_app(config_class=cConfig):
vApp.config.from_object(cConfig)
vDB.init_app(vApp)
vMigrate.init_app(vApp,vDB)
vJWT.init_app(vApp)


vApp.config["SQLALCHEMY_DATABASE_URI"] = DB_URI


# template_dir = vApp.root_path
# vApp = Flask(__name__, template_folder=template_dir)
@vApp.route("/")
def hello():   
    #template_dir = os.path.abspath('../../app')
    #vApp = Flask(__name__, template_folder=template_dir)
    #print(str(template_dir))
    print(str(DB_URI))
    print(str(template_dir2))
    print("dari root\ndari root\ndari root")
    #https://stackoverflow.com/questions/33396064/flask-template-not-found
    #https://stackoverflow.com/questions/31002890/how-to-reference-a-html-template-from-a-different-directory-in-python-flask
    
    #return "Hello, world. Aaaagain"
    #return render_template("exercise3-LogMasuk.html") 
    return redirect("/LogMasuk", code=302)
    

vFrontendBp = Blueprint('frontend', __name__, template_folder=template_dir2+'/app')
CORS(vFrontendBp)

@vFrontendBp.route("/HalMuka", methods=["GET"],strict_slashes=False)
def bukaHalmuka():
    return render_template("exercise3-HalMuka.html")

@vFrontendBp.route("/LogMasuk")
def gLogMasuk():
    return render_template("exercise3-LogMasuk.html") 

@vFrontendBp.route("/Daftar",methods=["GET"])
def gDaftar():
    return render_template("exercise3-Daftar.html")

@vFrontendBp.route("/LogMasuk",methods=["POST"],strict_slashes=False)
def pLogMasuk():
    vfData=request.get_json()
    vfSurel=vfData.get("email")
    vfKodepas=vfData.get("password")
    if not vfSurel or not vfKodepas:
        return jsonify({"message":"masukkan email dan kodepas (password)"}),404
    vdUser=cUsers.query.filter_by(vdSurel=vfSurel).first()
    if not vdUser:
        return jsonify({"message":"Pengguna ini belum terdaftar"})
    elif not check_password_hash(vdUser.vdKodepas,vfKodepas):
        return jsonify({"message":"kodepas tidak cocok (password salah)"}),400
    return jsonify({
        "message":"Bermasil masuk log",
        "access_token":create_access_token(identity=vdUser.vdIDUser),
        "refresh_token":create_refresh_token(identity=vdUser.vdIDUser)
    })
@vFrontendBp.route("/Daftar",methods=["POST"])
def pDaftar():
    vfData=request.get_json()
    vfNama=vfData.get("sNama")
    vfSurel=vfData.get("sSurel")
    vfKodepas=vfData.get("sKodepas")
    if not vfNama or not vfSurel or not vfKodepas:
        return jsonify({"message":"Masukkan nama, alamat surat elektronik (email), dan kodepas (password)"}),400
    try:
        tbhUser=cUsers(vdNama=vfNama,vdSurel=vfSurel,vdKodepas=generate_password_hash(vfKodepas))
        vDB.session.add(tbhUser)
        vDB.session.commit()
    except IntegrityError:
        return jsonify({"mesage":"Penguna sudah ada"}),400
    return jsonify({"message":"Pengguna baru berhasil dibuat"}),201


class cUsers(vDB.Model):
    vdIDUser = vDB.Column(vDB.Integer, primary_key=True)
    vdNama=vDB.Column(vDB.String(64),nullable=False)
    vdSurel=vDB.Column(vDB.String(128),unique=True,nullable=False)
    vdKodepas=vDB.Column(vDB.String(1024),nullable=False)
    #vdDibuat=vDB.column(vDB.DateTime, default=datetime.datetime.now())
    vrTasks=vDB.relationship('cTasks',back_populates='vrUser')
    def uSerialize(self):
        return{
            "idUser":self.vdIDUser,
            "nama":self.vdNama,
            "surel":self.vdSurel,
            "tugas":[serTask.tSerialize() for serTask in self.vrTasks]
        }

class cTasks(vDB.Model):
    vdIDTask=vDB.Column(vDB.Integer, primary_key=True)
    vdJudul=vDB.Column(vDB.String(64))
    vdRinci=vDB.Column(vDB.String(1024))
    vdStatus=vDB.Column(vDB.Boolean, default = False)     
    vrUser=vDB.relationship('cUsers',back_populates='vrTasks')
    user_id=vDB.Column(vDB.Integer, vDB.ForeignKey('c_users.vdIDUser'))
    def tSerialize(self): #note: nama disini nanti jadi name:value pair saat GET dan POST di routes.py task dan user?
        return{
            "idTask":self.vdIDTask,
            "Judul-Task":self.vdJudul,
            "Rincian-Task":self.vdRinci,
            "status":self.vdStatus,
            "idUser":self.user_id
        }


if __name__ == "__main__":
    vApp.run(host='0.0.0.0')

vApp.register_blueprint(vFrontendBp, url_prefix='/')
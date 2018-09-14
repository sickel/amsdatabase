import os
import pyodbc
from xlrd import open_workbook
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, Response,send_from_directory,jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user ,current_user
import platform
from ams.dbconnector import dbconnector
from ams.uploadfile import csvfile
from werkzeug import secure_filename
from inspect import currentframe, getframeinfo
# print(getframeinfo(currentframe()).lineno)



if platform.system()=='Windows':
	UPLOAD_FOLDER = 'c:/windows/temp/'
else:
	UPLOAD_FOLDER = '/tmp'
	
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(
    SECRET_KEY = os.urandom(12)
)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

@app.route("/process", methods=['GET', 'POST'])
def process():
    req=dict(request.form)
    db=dbconnector()
    db.connecttodb()
    utm=req['UTMzone'][0]
    if request.form["project_new"] != '':
        name=request.form["project_new"]
        try:
            sql="insert into project (name) values(?)"
            db.insert(sql,name)
        except pyodbc.IntegrityError:
            pass # takes care of this in next line
        projectid=db.name2id(name,"project")
        req['project']=[projectid] # must be a list to make it compatible with a selected project
        # sql="create view "+project_vv+" as select * from
        projectname=name
        viewname="Project_"+projectname.replace(" ","_")
        sql="create view "+viewname+" as select measurement.* from measurement right join datafile on datafile.id=datafileid right join survey on surveyid=survey.id where survey.projectid="+str(projectid)
        db.cursor.execute(sql)
        sql="insert into geometry_columns values('ams','dbo',?,'location_utm',2,326"+utm+",'POINT')"
        db.cursor.execute(sql,[viewname])
        db.cursor.commit()
    else:
        projectid=request.form["project"]
        projectname=db.id2name(projectid,"project")
    if request.form["survey_new"] != '':
        name=request.form["survey_new"]
        sql="insert into survey (name,projectid,systemid) values(?,?,?)"
        try:
            db.insert(sql,[name,projectid,request.form["system"]])
        except pyodbc.IntegrityError:
            pass # takes care of this in next line
        surveyid=db.name2id(name,"survey")
        req['survey']=[surveyid] # must be a list to make it compatible with a selected survey
        surveyname=name
        viewname="Survey_"+projectname.replace(" ","_")+"_"+surveyname.replace(" ","_")
        sql="create view "+viewname+" as select measurement.* from measurement right join datafile on datafile.id=datafileid where datafile.surveyid="+str(surveyid)
        db.cursor.execute(sql)
        sql="insert into geometry_columns values('ams','dbo',?,'location_utm',2,326"+utm+",'POINT')"
        db.cursor.execute(sql,[viewname])
        db.cursor.commit()
    else:
        surveyid=request.form["survey"]
        surveyname=db.id2name(surveyid,"survey")
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath =os.path.join(app.config['UPLOAD_FOLDER'], filename) 
            file.save(filepath)
            uploadfile=csvfile(filepath,req)
            if not(uploadfile.finished):
                print("starting")
                uploadfile.importdata()
                

    return(str(request.form)+'<a href="/">back</a>')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    vds=['VD1','VD2','VD3','VD4']
    system=dbconnector()
    system.connecttodb()
    systems=system.listnames('system')
    projects=system.listnames('project')
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            return redirect(url_for('/'))

    return render_template('upload.html', title="Last opp csv-fil",vds=vds,systems=systems,projects=projects)


@app.route("/None")
@app.route("/")
def home():
    return render_template('template.html',title="Database for mobile målinger")


@app.route("/about")
def about():
    return render_template('about.html', title="Om")

@app.errorhandler(404)
def page_not_found2(e):
    return Response('<p>Denne siden finnes ikke...</p><p><a href="/">Tilbake</a>')
    #return render_template('htmlerror.html')
        
 
# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Ugyldig bruker</p><p><a href="/">Tilbake</a>')

@app.route('/ajax/detectors',methods=["GET", "POST"])
def detectors():
    system=dbconnector()
    system.connecttodb()
    print(request.args)
    systemid=request.args.get('systemid')
    systems=system.fetchdict('select id,name from detector where systemid=?',params=systemid)
    return(jsonify(systems))

# TODO: Rewrite to common eventhandler
    
@app.route('/ajax/surveys',methods=["GET", "POST"])
def surveys():
    system=dbconnector()
    system.connecttodb()
    print(request.args)
    projectid=request.args.get('projectid')
    systems=system.fetchdict('select id,name from survey where projectid=?',params=projectid)
    return(jsonify(systems))

    
if __name__ == '__main__':
        
    app.secret_key = os.urandom(12)
    app.run(debug=True)

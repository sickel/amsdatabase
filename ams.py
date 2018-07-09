import os
from xlrd import open_workbook
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, Response,send_from_directory,jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user ,current_user
import platform
from ams.dbconnector import dbconnector

if platform.system()=='Windows':
	UPLOAD_FOLDER = 'c:/windows/temp/'
else:
	UPLOAD_FOLDER = '/tmp'
	
ALLOWED_EXTENSIONS = set(['csv'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(
    SECRET_KEY = os.urandom(12)
)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True



@app.route("/upload", methods=['GET', 'POST'])
def upload():
    vds=['VD1','VD2','VD3','VD4']
    system=dbconnector()
    system.connecttodb()
    systems=system.listnames('system')
    projects=system.listnames('project')
    print(projects)
    if request.method == 'POST':
    
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))

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

    
if __name__ == '__main__':
        
    app.secret_key = os.urandom(12)
    app.run(debug=True)

from flask import Flask, request
from flask_cors import CORS
from apis.prof_api import prof_bp
from apis.student_api import student_bp
from apis.exercise_api import exercise_bp
from apis.stud_exe_api import stud_exe_bp
from apis.stud_prof_api import stud_prof_bp
from apis.auth_api import auth_bp
from apis.smol_api import smol_api
from utils.seed_data import seed_data
from llm.smol.smol_instance import smol

app = Flask(__name__)

# Restrictive CORS configuration
CORS(app, 
     origins=["http://localhost:3039", "http://127.0.0.1:3039"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True,
     expose_headers=["Content-Type", "Authorization"])

# Register blueprints
app.register_blueprint(prof_bp)
app.register_blueprint(student_bp)
app.register_blueprint(exercise_bp)
app.register_blueprint(stud_exe_bp)
app.register_blueprint(stud_prof_bp)
app.register_blueprint(smol_api)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

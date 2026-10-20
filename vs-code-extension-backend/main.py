import argparse
import os
from flask import Flask, request
from flask_cors import CORS
from apis.prof_api import prof_bp
from apis.student_api import student_bp
from apis.exercise_api import exercise_bp
from apis.stud_exe_api import stud_exe_bp
from apis.stud_prof_api import stud_prof_bp
from apis.auth_api import auth_bp
from apis.smol_api import smol_api
from apis.tutor_api import tutor_bp
from utils.seed_data import seed_data
from llm.smol.smol_instance import smol
from llm import backend

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
app.register_blueprint(tutor_bp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Code-Hinter backend")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 5000)))
    parser.add_argument("--offline", action="store_true", help="no LLM: rule-based tutor only (fast, CPU-friendly)")
    args = parser.parse_args()
    if args.offline:
        os.environ["CH_LLM_BACKEND"] = "offline"
    if backend.llm_available():
        smol.load()  # load the weights once at startup instead of on the first request
    app.run(host='0.0.0.0', port=args.port, debug=True, use_reloader=False)

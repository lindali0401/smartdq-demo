from flask import render_template, request, redirect, url_for, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User
from app import app, babel, login_manager, db
from flask_babel import get_locale, _
from werkzeug.security import check_password_hash
import pandas as pd
from werkzeug.utils import secure_filename
import datetime

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    session['lang'] = lang_code
    return redirect(request.referrer or url_for('home'))

@app.route('/')
def home():
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
       

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        else:
            return render_template("login.html", error=_("Falscher Benutzername oder Passwort"), username=username)

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return render_template("register.html", error=_("Passwörter stimmen nicht überein"), username=username)

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error=_("Benutzername bereits vergeben"), username=username)

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect('/')

    return render_template("register.html")


@app.context_processor
def inject_locale():
    return {'current_locale': str(get_locale())}


@app.route("/chatbot")
@login_required
def chat():
    return render_template("chatbot.html")



ALLOWED_EXTENSIONS = {'csv'}
global_last_summary = {}
global_low_dimensions = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        try:
            df = pd.read_csv(file)

            total_cells = df.shape[0] * df.shape[1]
            missing_values = int(df.isnull().sum().sum())
            completeness = round(1 - (missing_values / total_cells), 4)

            summary = {
                "filename": filename,
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
                "missing_values": missing_values,
                "completeness": completeness
            }

            # rules
            low_dimensions = []

            # 1. Completeness
            if completeness < 0.85:
                low_dimensions.append("Completeness")

            # 2. Consistency
            if df.duplicated().sum() > 0:
                low_dimensions.append("Consistency")

            # 3. Traceability
            if not any("id" in col.lower() or "zeit" in col.lower() or "time" in col.lower() for col in df.columns):
                low_dimensions.append("Traceability")

            # 4. Understandability
            if all(len(col.strip()) <= 3 for col in df.columns):
                low_dimensions.append("Understandability")

            # 5. Currentness
            date_cols = [col for col in df.columns if "date" in col.lower() or "zeit" in col.lower() or "time" in col.lower()]
            if date_cols:
                try:
                    latest_time = pd.to_datetime(df[date_cols[0]], errors='coerce').max()
                    if pd.isnull(latest_time) or (datetime.datetime.now() - latest_time).days > 90:
                        low_dimensions.append("Currentness")
                except:
                    low_dimensions.append("Currentness")
            else:
                low_dimensions.append("Currentness")

            # 可继续添加 Efficiency, Precision 等逻辑...

            # # 保存到 session（后续 Rasa 可访问）
            # session['last_summary'] = summary
            # session['low_dimensions'] = low_dimensions
            global global_last_summary, global_low_dimensions
            global_last_summary = summary
            global_low_dimensions = low_dimensions

            return jsonify({
                "summary": summary,
                "low_dimensions": low_dimensions
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file format"}), 400

@app.route('/summary', methods=['GET'])
def get_summary():
    global global_last_summary, global_low_dimensions

    if global_last_summary:
        return jsonify({
            "summary": global_last_summary,
            "low_dimensions": global_low_dimensions
        }), 200
    return jsonify({"error": "No summary available"}), 404



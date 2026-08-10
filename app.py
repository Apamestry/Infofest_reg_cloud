from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Update credentials to match your MySQL setup: 'mysql+pymysql://username:password@localhost/database_name'
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# --- DB config comes from environment variables, set at `docker run` time ---
# Read environment variables (falls back to defaults if not set)
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "flask_db")

# Construct MySQL URI dynamically
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        if name and email:
            new_user = User(name=name, email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))

    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
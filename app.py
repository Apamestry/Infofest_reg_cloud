import os
from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# --- DB config comes from environment variables, set at `docker run` time ---
DB_USER = os.environ.get("DB_USER", "root")
# URL-encode the password so special characters like '@' don't break the URI parsing
DB_PASSWORD = quote_plus(os.environ.get("DB_PASSWORD", "password"))
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "flask_db")

# Construct MySQL URI dynamically and actually assign it to Flask's config
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
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
    app.run(host='0.0.0.0', debug=True)
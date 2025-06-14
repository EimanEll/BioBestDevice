import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Initialize Flask and SQLAlchemy
db = SQLAlchemy()

def init_app(app: Flask):
    # Configure SQLite database
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'mri_guide.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    # Create tables if not exist
    with app.app_context():
        db.create_all()
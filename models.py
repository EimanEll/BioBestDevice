from database import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255))
    models = db.relationship('Model', backref='vendor', lazy=True)

class Model(db.Model):
    __tablename__ = 'models'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    field_strength = db.Column(db.Float)
    bore_type = db.Column(db.String(100))
    gradient_strength = db.Column(db.Float)
    cryogen_type = db.Column(db.String(100))
    patient_table = db.Column(db.String(255))
    rf_coils = db.Column(db.Text)
    software_features = db.Column(db.Text)
    cost_estimate = db.Column(db.Float)
    service_contract = db.Column(db.String(255))
    energy_consumption = db.Column(db.Float)
    footprint = db.Column(db.String(100))
    additional_info = db.Column(db.Text)

class Criteria(db.Model):
    __tablename__ = 'criteria'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    inputs = db.relationship('UserInput', backref='session', lazy=True)
    weights = db.relationship('Weight', backref='session', lazy=True)
    scores = db.relationship('ModelScore', backref='session', lazy=True)
    recommendation = db.relationship('Recommendation', backref='session', uselist=False)

class UserInput(db.Model):
    __tablename__ = 'user_inputs'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    criteria_id = db.Column(db.Integer, db.ForeignKey('criteria.id'), nullable=False)
    value = db.Column(db.String(255))
    criteria = db.relationship('Criteria')

class Weight(db.Model):
    __tablename__ = 'weights'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    criteria_id = db.Column(db.Integer, db.ForeignKey('criteria.id'), nullable=False)
    weight = db.Column(db.Float)
    criteria = db.relationship('Criteria')

class ModelScore(db.Model):
    __tablename__ = 'model_scores'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    score = db.Column(db.Float)
    model = db.relationship('Model')

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    rationale = db.Column(db.Text)
    model = db.relationship('Model')
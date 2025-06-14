from app import app
from database import db
from models import Vendor, Model, Criteria
with app.app_context():
    # Exemples
    v1 = Vendor(name='GE Healthcare', country='USA')
    db.session.add(v1)
    v2 = Vendor(name='Siemens Healthineers', country='Germany')
    db.session.add(v2)
    # ... idem pour d'autres
    db.session.commit()
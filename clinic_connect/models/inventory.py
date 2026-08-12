from clinic_connect.database import db

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    unit_price = db.Column(db.Float, default=0.0, nullable=False)
    min_threshold = db.Column(db.Integer, default=10, nullable=False)

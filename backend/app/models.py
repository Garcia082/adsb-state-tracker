from . import db

class Aeronave(db.Model):
    __tablename__ = "aeronaves"

    icao24    = db.Column(db.String(6),  primary_key=True)
    callsign  = db.Column(db.String(10))
    lat       = db.Column(db.Float)
    lon       = db.Column(db.Float)
    alt       = db.Column(db.Integer)
    vel       = db.Column(db.Integer)
    is_state  = db.Column(db.Boolean)
    last_seen = db.Column(db.DateTime)

class VueloDiplomatico(db.Model):
    __tablename__ = "vuelos_diplomaticos"

    id             = db.Column(db.Integer, primary_key=True)
    icao24         = db.Column(db.String(6), db.ForeignKey("aeronaves.icao24"))
    autorizacion   = db.Column(db.String(20), nullable=False)
    validez_desde  = db.Column(db.DateTime, nullable=False)
    validez_hasta  = db.Column(db.DateTime, nullable=False)
    casilla18      = db.Column(db.Text, nullable=False)

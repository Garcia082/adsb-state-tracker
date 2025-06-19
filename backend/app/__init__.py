from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER','root')}:"
        f"{os.getenv('MYSQL_PASSWORD','root')}@"
        f"{os.getenv('MYSQL_HOST','db')}/adsb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .models import Aeronave, VueloDiplomatico

    @app.route("/api/health")
    def health():
        return jsonify(status="ok")

    @app.route("/api/aeronaves")
    def listar_aeronaves():
        ahora = datetime.utcnow()
        hace_60s = ahora - timedelta(seconds=60)

        regs = (Aeronave.query
                       .filter(Aeronave.last_seen >= hace_60s)
                       .all())
        return jsonify([{
            "icao24": a.icao24,
            "callsign": a.callsign,
            "lat": a.lat, "lon": a.lon,
            "alt": a.alt, "vel": a.vel,
            "is_state": bool(a.is_state)
        } for a in regs])

    @app.route("/api/autorizacion/<icao24>")
    def autorizacion(icao24):
        ahora = datetime.utcnow()
        vuelo = (
            VueloDiplomatico.query
            .filter_by(icao24=icao24.lower())
            .filter(VueloDiplomatico.validez_desde <= ahora,
                    VueloDiplomatico.validez_hasta >= ahora)
            .order_by(VueloDiplomatico.validez_hasta.desc())
            .first()
        )
        if vuelo is None:
            return jsonify(
                icao24=icao24.lower(),
                autorizacion="NO_ENCONTRADA",
                valido=False,
                detalle=None
            ), 404
        
        return jsonify(
            icao24=vuelo.icao24,
            autorizacion=vuelo.autorizacion,
            valido=True,
            desde=vuelo.validez_desde.isoformat(),
            hasta=vuelo.validez_hasta.isoformat(),
            casilla18=vuelo.casilla18,
        )

    # ----------- 404 JSON para /api/* -----------------
    @app.errorhandler(404)
    def _api_404(e):
        if request.path.startswith("/api/"):
            return jsonify(
                error="NOT_FOUND",
                path=request.path,
                mensaje="Recurso no encontrado"
            ), 404
        return e
    # --------------------------------------------------
  
    return app

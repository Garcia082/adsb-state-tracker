import os, time, requests, pymysql, logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

# ---------- OAuth2 (Client-Credentials) ----------------------------------
TOKEN_URL = (
    "https://auth.opensky-network.org/"
    "auth/realms/opensky-network/protocol/openid-connect/token"
)
CLIENT_ID  = os.getenv("OPENSKY_CLIENT_ID")
CLIENT_SEC = os.getenv("OPENSKY_CLIENT_SECRET")
TOKEN      = None
EXPIRES_AT = datetime.utcnow()

def get_token():
    """Devuelve un token válido, renovándolo si es necesario."""
    global TOKEN, EXPIRES_AT
    if TOKEN and datetime.utcnow() < EXPIRES_AT:
        return TOKEN

    resp = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SEC,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    TOKEN = data["access_token"]
    EXPIRES_AT = datetime.utcnow() + timedelta(seconds=data["expires_in"] - 60)
    logging.info("Token nuevo; expira %s", EXPIRES_AT.isoformat())
    return TOKEN
# ------------------------------------------------------------------------

API = (
    "https://opensky-network.org/api/states/all"
    "?lamin=35&lomin=-10&lamax=45&lomax=5"
)

def conn():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        database="adsb",
        autocommit=True,
    )

def es_estado(h):   # ejemplo simple
    return h[:2].upper() in {"AE", "AD", "AF"}

def ciclo():
    while True:
        try:
            hdrs = {"Authorization": f"Bearer {get_token()}"}
            r = requests.get(API, headers=hdrs, timeout=10)
            r.raise_for_status()
            estados = r.json()["states"]
            db = conn()
            with db.cursor() as cur:
                for s in estados:
                    if s[5] is None:
                        continue
                    cur.execute(
                        """REPLACE INTO aeronaves
                           (icao24,callsign,lat,lon,alt,vel,is_state,last_seen)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (
                            s[0],
                            (s[1] or "").strip() or None,
                            float(s[6]),
                            float(s[5]),
                            int(s[13] or 0),
                            int(s[9] or 0),
                            es_estado(s[0]),
                            datetime.utcnow(),
                        ),
                    )
            logging.info("Insertados %d registros", len(estados))
        except Exception as e:
            logging.exception("Error integrador: %s", e)
        time.sleep(30)

if __name__ == "__main__":
    ciclo()

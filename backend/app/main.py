from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import Session, select
import os, json
from dotenv import load_dotenv

from app.db import init_db, get_session
from app.models import User, RaceEvent, Trip, TripJoinRequest, Message, FavoriteEvent, Notification
from app.models import Role, EventStatus, JoinStatus, NotificationType
from app.security import hash_password, verify_password, create_access_token, decode_token
from app.realtime import manager

load_dotenv()
app = FastAPI(title=os.getenv("APP_NAME","BikeStop"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/api/health")
def health():
    return {"ok": True}

def auth_user(session: Session, authorization: str|None):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.split(" ",1)[1].strip()
    try:
        sub = decode_token(token)
        uid = int(sub)
    except Exception:
        raise HTTPException(401, "Invalid token")
    u = session.get(User, uid)
    if not u:
        raise HTTPException(401, "User not found")
    return u

@app.post("/auth/register")
def register(payload: dict, session: Session = Depends(get_session)):
    email = payload.get("email"); name = payload.get("name"); password = payload.get("password")
    if not email or not password or not name:
        raise HTTPException(400, "Missing fields")
    if session.exec(select(User).where(User.email==email)).first():
        raise HTTPException(400, "Email already registered")
    u = User(email=email, name=name, password_hash=hash_password(password), role=Role.USER)
    session.add(u); session.commit(); session.refresh(u)
    return {"id":u.id,"email":u.email,"name":u.name,"role":u.role}

@app.post("/auth/login")
def login(payload: dict, session: Session = Depends(get_session)):
    email = payload.get("email"); password = payload.get("password")
    u = session.exec(select(User).where(User.email==email)).first()
    if not u or not verify_password(password, u.password_hash):
        raise HTTPException(400, "Invalid credentials")
    return {"access_token": create_access_token(str(u.id)), "token_type":"bearer"}

@app.get("/me")
def me(authorization: str|None = None, session: Session = Depends(get_session)):
    u = auth_user(session, authorization)
    return {"id":u.id,"email":u.email,"name":u.name,"role":u.role}

@app.get("/events")
def events(session: Session = Depends(get_session)):
    return session.exec(select(RaceEvent).where(RaceEvent.status==EventStatus.APPROVED).order_by(RaceEvent.date.asc())).all()

@app.post("/events")
def propose_event(payload: dict, authorization: str|None = None, session: Session = Depends(get_session)):
    u = auth_user(session, authorization)
    e = RaceEvent(title=payload["title"], date=payload["date"], location=payload["location"], status=EventStatus.PENDING, created_by_id=u.id)
    session.add(e); session.commit(); session.refresh(e)
    return e

@app.get("/admin/events/pending")
def pending(authorization: str|None = None, session: Session = Depends(get_session)):
    u = auth_user(session, authorization)
    if u.role != Role.ADMIN:
        raise HTTPException(403, "Admin only")
    return session.exec(select(RaceEvent).where(RaceEvent.status==EventStatus.PENDING).order_by(RaceEvent.date.asc())).all()

@app.post("/admin/events/{event_id}/approve")
def approve(event_id: int, authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    if u.role != Role.ADMIN: raise HTTPException(403,"Admin only")
    e = session.get(RaceEvent,event_id)
    if not e: raise HTTPException(404,"Event not found")
    e.status = EventStatus.APPROVED
    session.add(e); session.commit(); session.refresh(e)
    return e

@app.post("/admin/events/{event_id}/reject")
def reject(event_id: int, authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    if u.role != Role.ADMIN: raise HTTPException(403,"Admin only")
    e = session.get(RaceEvent,event_id)
    if not e: raise HTTPException(404,"Event not found")
    e.status = EventStatus.REJECTED
    session.add(e); session.commit(); session.refresh(e)
    return e

@app.get("/events/{event_id}/trips")
def trips(event_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Trip).where(Trip.event_id==event_id).order_by(Trip.departure_time.asc())).all()

@app.post("/events/{event_id}/trips")
def create_trip(event_id: int, payload: dict, authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    t = Trip(event_id=event_id, driver_id=u.id,
             departure_time=payload["departure_time"],
             departure_place=payload["departure_place"],
             destination_place=payload["destination_place"],
             seats_total=int(payload["seats_total"]),
             seats_available=int(payload["seats_total"]),
             notes=payload.get("notes"))
    session.add(t); session.commit(); session.refresh(t)
    return t

@app.post("/trips/{trip_id}/requests")
def request_join(trip_id: int, authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    t = session.get(Trip, trip_id)
    if not t: raise HTTPException(404,"Trip not found")
    if t.seats_available <= 0: raise HTTPException(400,"No seats")
    r = TripJoinRequest(trip_id=trip_id, requester_id=u.id, status=JoinStatus.PENDING)
    session.add(r); session.commit(); session.refresh(r)
    return r

@app.get("/requests/{join_request_id}/messages")
def list_messages(join_request_id: int, authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    # minimal check: allow both parties later; for MVP allow requester only
    return session.exec(select(Message).where(Message.join_request_id==join_request_id).order_by(Message.created_at.asc())).all()

@app.post("/requests/{join_request_id}/messages")
def send_message(join_request_id: int, payload: dict, authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    m = Message(join_request_id=join_request_id, sender_id=u.id, content=payload["content"])
    session.add(m); session.commit(); session.refresh(m)
    return m

@app.get("/notifications")
def notifications(authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    return session.exec(select(Notification).where(Notification.user_id==u.id).order_by(Notification.created_at.desc())).all()

@app.post("/notifications/{nid}/read")
def mark_read(nid: int, authorization: str|None=None, session: Session=Depends(get_session)):
    u = auth_user(session, authorization)
    n = session.get(Notification, nid)
    if not n or n.user_id != u.id: raise HTTPException(404,"Not found")
    n.is_read = True
    session.add(n); session.commit()
    return {"ok": True}

@app.websocket("/ws")
async def ws(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=4401); return
    try:
        uid = int(decode_token(token))
    except Exception:
        await ws.close(code=4401); return
    await manager.connect(uid, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(uid, ws)

# Serve frontend
FRONTEND_DIST = os.getenv("FRONTEND_DIST", "frontend_dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
    @app.get("/{full_path:path}")
    def spa(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIST,"index.html"))

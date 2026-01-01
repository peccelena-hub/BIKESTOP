from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class EventStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class JoinStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class NotificationType(str, Enum):
    NEW_MESSAGE = "NEW_MESSAGE"
    NEW_TRIP_ON_FAVORITE_EVENT = "NEW_TRIP_ON_FAVORITE_EVENT"
    NEW_JOIN_REQUEST = "NEW_JOIN_REQUEST"
    JOIN_REQUEST_STATUS = "JOIN_REQUEST_STATUS"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    password_hash: str
    role: Role = Field(default=Role.USER)

class RaceEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    date: datetime
    location: str
    status: EventStatus = Field(default=EventStatus.PENDING)
    created_by_id: int = Field(foreign_key="user.id")

class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="raceevent.id")
    driver_id: int = Field(foreign_key="user.id")
    departure_time: datetime
    departure_place: str
    destination_place: str
    seats_total: int
    seats_available: int
    notes: Optional[str] = None

class TripJoinRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    requester_id: int = Field(foreign_key="user.id")
    status: JoinStatus = Field(default=JoinStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    join_request_id: int = Field(index=True)
    sender_id: int
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FavoriteEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    event_id: int = Field(foreign_key="raceevent.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    type: NotificationType
    title: str
    body: str
    payload_json: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

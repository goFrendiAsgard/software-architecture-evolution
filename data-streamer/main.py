from typing import Mapping
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

import datetime
import uuid
import os
import traceback
import transport

connection_string = os.getenv('BACKEND_SQLALCHEMY_DATABASE_URL', 'sqlite://')
engine = create_engine(connection_string)
Base = declarative_base()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
mb_config = {
    'message_bus_type': os.getenv('BACKEND_MESSAGE_BUS_TYPE', 'local'),
    'rabbitmq_host' : os.getenv('BACKEND_RABBITMQ_HOST', 'localhost'),
    'rabbitmq_user' : os.getenv('BACKEND_RABBITMQ_USER', 'root'),
    'rabbitmq_pass' : os.getenv('BACKEND_RABBITMQ_PASS', 'toor'),
    'rabbitmq_vhost' : os.getenv('BACKEND_RABBITMQ_VHOST', '/'),
}
mb: transport.MessageBus = transport.init_mb(mb_config)

class SavedPokemonVote(Base):
    __tablename__ = 'saved_pokemon_vote'
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36))
    day_bucket = Column(Date, index=True)
    name = Column(String(20), index=True)
    voted_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

def save_pokemon_vote(engine: Engine, pokemon_vote: SavedPokemonVote):
    pokemon_vote.day_bucket = pokemon_vote.voted_at.date()
    session = Session(bind=engine)
    session.add(pokemon_vote)
    session.commit()
    session.refresh(pokemon_vote)
    session.close()

@transport.handle(mb, 'new_vote_saved')
def handle_new_vote(message) -> Mapping[str, str]:
    try:
        request_id = message['request_id']
        pokemon_name = message['pokemon_name']
        voted_at = message['voted_at']
        pokemon_vote = SavedPokemonVote(request_id=request_id, name=pokemon_name, voted_at=voted_at)
        save_pokemon_vote(engine, pokemon_vote)
    except:
        print(traceback.format_exc())
        return None

@app.on_event('shutdown')
def on_shutdown():
    mb.shutdown()
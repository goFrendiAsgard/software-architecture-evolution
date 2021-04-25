from typing import Mapping
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy import Boolean, Column, Integer, String, DateTime
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

class PokemonVote(Base):
    __tablename__ = 'pokemon_vote'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20))
    voted_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def vote_pokemon(engine: Engine, pokemon_name: str) -> PokemonVote:
    session = Session(bind=engine)
    pokemon_vote = PokemonVote(name=pokemon_name)
    session.add(pokemon_vote)
    session.commit()
    session.refresh(pokemon_vote)
    session.close()
    return pokemon_vote

@transport.handle(mb, 'new_vote')
def handle_new_vote(message) -> Mapping[str, str]:
    try:
        request_id = message['request_id']
        pokemon_name = message['pokemon_name']
        vote = vote_pokemon(engine, pokemon_name)
        mb.publish('new_vote_saved', {
            'request_id': request_id,
            'pokemon_name': pokemon_name,
            'voted_at': vote.voted_at,
        })
    except:
        print(traceback.format_exc())
        return None

@app.on_event('shutdown')
def on_shutdown():
    mb.shutdown()
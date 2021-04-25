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

def get_vote_result(engine: Engine) -> Mapping[str, str]:
    sql = 'SELECT name, count(id) AS vote FROM pokemon_vote GROUP BY name'
    connection = engine.connect()
    pokemon_vote_result_list = connection.execute(text(sql))
    result = {}
    for pokemon_vote_result in pokemon_vote_result_list:
        pokemon_name = pokemon_vote_result[0]
        vote = pokemon_vote_result[1]
        result[pokemon_name] = vote
    connection.close()
    return result

@transport.handle_rpc(mb, 'get_vote_result')
def handle_get_vote_result() -> Mapping[str, str]:
    try: 
        result = get_vote_result(engine)
        return result
    except:
        print(traceback.format_exc())
        return None
    

@app.on_event('shutdown')
def on_shutdown():
    mb.shutdown()
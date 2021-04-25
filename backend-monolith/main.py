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
import os
import traceback

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

class PokemonVote(Base):
    __tablename__ = 'pokemon_vote'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20))
    voted_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def vote_pokemon(engine: Engine, pokemon_name: str):
    session = Session(bind=engine)
    pokemon_vote = PokemonVote(name=pokemon_name)
    session.add(pokemon_vote)
    session.commit()
    session.close()
    return {'detail': 'Success'}

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

@app.post('/vote/{pokemon_name}', response_model=Mapping[str, str])
def vote_pokemon_route(pokemon_name: str):
    try:
        vote_pokemon(engine, pokemon_name)
        return {'detail': 'Success'}
    except:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail='Internal server error')

@app.get('/vote', response_model= Mapping[str, str])
def get_vote_result_route():
    try:
        return get_vote_result(engine)
    except:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail='Internal server error')

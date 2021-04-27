from typing import Mapping
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

import datetime
import os

connection_string = os.getenv('CONNECTION_STRING', 'sqlite://')
engine = create_engine(connection_string)
Base = declarative_base()

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

def get_vote_result(engine: Engine) -> Mapping[str, str]:
    sql = 'SELECT name, count(id) AS vote FROM pokemon_vote GROUP BY name'
    connection = engine.connect()
    pokemon_vote_result_list = connection.execute(text(sql))
    results = []
    for pokemon_vote_result in pokemon_vote_result_list:
        pokemon_name = pokemon_vote_result[0]
        vote = pokemon_vote_result[1]
        results.append('{pokemon_name}\t: {vote}'.format(pokemon_name=pokemon_name, vote=vote))
    connection.close()
    return '\n'.join(results)

while True:
    print('== POKEMON VOTER')
    print('1. Show Vote')
    print('2. Vote Pokemon')
    print('3. Exit')
    user_choice = input('Choose action: ')
    print("Your action choice was: {}".format(user_choice))
    if user_choice == '1':
        print(get_vote_result(engine))
    elif user_choice == '2':
        pokemon_name = input('Pokemon name: ')
        vote_pokemon(engine, pokemon_name)
    elif user_choice == '3':
        print('Exiting program')
        break
    else:
        print('Invalid action choice')
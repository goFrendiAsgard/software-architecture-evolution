from typing import Mapping
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

import uuid
import datetime
import random
import os
import math

connection_string = os.getenv('CONNECTION_STRING', 'sqlite://')
engine = create_engine(connection_string)
Base = declarative_base()

class SavedPokemonVote(Base):
    __tablename__ = 'saved_pokemon_vote'
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36))
    day_bucket = Column(Date, index=True)
    name = Column(String(20), index=True)
    voted_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

def generate(engine: Engine, pokemon_name: str, m: int, c: int, day_interval: int):
    noise_range = 5
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(day_interval)
    for x in range(day_interval):
        current_date = start_date + datetime.timedelta(x)
        y = math.ceil( m * x + c + random.randint(-noise_range, noise_range))
        voted_at = current_date
        day_bucket = current_date
        session = Session(bind=engine)
        for row_index in range(y):
            request_id = uuid.uuid4()
            new_vote = SavedPokemonVote(
                request_id=request_id,
                day_bucket=day_bucket,
                name=pokemon_name,
                voted_at=voted_at
            )
            print(new_vote)
            session.add(new_vote)
        session.commit()
        session.close()


generate(engine, pokemon_name='mewtwo', m=3, c=20, day_interval=120)
generate(engine, pokemon_name='snorlax', m=3, c=10, day_interval=120)
generate(engine, pokemon_name='koffing', m=-1, c=200, day_interval=120)
    
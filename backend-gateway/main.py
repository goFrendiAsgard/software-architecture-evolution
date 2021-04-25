from typing import Mapping
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import datetime
import uuid
import os
import traceback
import transport

mb_config = {
    'message_bus_type': os.getenv('BACKEND_MESSAGE_BUS_TYPE', 'local'),
    'rabbitmq_host' : os.getenv('BACKEND_RABBITMQ_HOST', 'localhost'),
    'rabbitmq_user' : os.getenv('BACKEND_RABBITMQ_USER', 'root'),
    'rabbitmq_pass' : os.getenv('BACKEND_RABBITMQ_PASS', 'toor'),
    'rabbitmq_vhost' : os.getenv('BACKEND_RABBITMQ_VHOST', '/'),
}
mb: transport.MessageBus = transport.init_mb(mb_config)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('shutdown')
def on_shutdown():
    mb.shutdown()

@app.post('/vote/{pokemon_name}', response_model=Mapping[str, str])
def vote_pokemon_route(pokemon_name: str):
    try:
        mb.publish('new_vote', {
            'request_id': uuid.uuid4(),
            'pokemon_name': pokemon_name,
        })
        return {'detail': 'Success'}
    except:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail='Internal server error')

@app.get('/vote', response_model= Mapping[str, str])
def get_vote_result_route():
    try:
        vote_result = mb.call_rpc('get_vote_result')
        return vote_result
    except:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail='Internal server error')

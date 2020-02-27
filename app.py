from pymongo import MongoClient
from pymongo.collection import ReturnDocument
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import make_response
from uuid import uuid4
import mongo_cfg


# Jinja asetukset muutettu jottei sekoitu vuen kanssa
class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))
app = CustomFlask(__name__)
#app = Flask(__name__)


@app.route('/')
def hello():
    resp = make_response(render_template('index.html'))
    if 'playerid' in request.cookies:
        pass
    else:
        newplr = create_player().get_json()
        expire = 360 * 60 * 60 * 24
        resp.set_cookie('playerid', newplr['pid'], max_age=expire)

    return resp


# Pelin tilanne
@app.route('/get_state/', methods=['POST'])
def get_state():
    player_id = request.cookies.get('playerid')

    client = MongoClient(mongo_cfg.mongo_url)
    db = client.get_default_database()

    collection = db.players
    player = collection.find_one({'id': player_id})

    return jsonify(score=player['score'])


@app.route('/create_player', methods=['POST'])
def create_player():
    client = MongoClient(mongo_cfg.mongo_url)
    db = client.get_default_database()

    collection = db.players

    newid = str(uuid4())
    new_player = {"id": newid, "score": 20}
    collection.insert_one(new_player)

    return jsonify(pid=newid)


@app.route('/reset_player/', methods=['POST'])
@app.route('/reset_player/<player_id>', methods=['POST'])
def reset_player(player_id=None):
    if player_id is None:
        player_id = request.cookies.get('playerid')

    client = MongoClient(mongo_cfg.mongo_url)
    db = client.get_default_database()

    collection = db.players
    player = collection.find_one_and_update({'id': player_id}, {'$set': {'score': 20}}, return_document=ReturnDocument.AFTER)

    return jsonify(score=player['score'])


# Kutsutaan nappia painaessa.
@app.route('/play/', methods=['POST'])
@app.route('/play/<player_id>', methods=['POST'])
def play_game(player_id=None):
    if player_id is None:
        player_id = request.cookies.get('playerid')

    client = MongoClient(mongo_cfg.mongo_url)
    db = client.get_default_database()

    collection = db.players
    player = collection.find_one_and_update({'id': player_id}, {'$inc': {'score': -1}}, return_document=ReturnDocument.AFTER)
    collection = db.game_state
    g_state = collection.find_one_and_update({}, {'$inc': {'clicks': 1}}, return_document=ReturnDocument.AFTER)

    clickno = g_state['clicks']
    reward = 0
    if clickno % 500 == 0:
        reward = 250
    elif clickno % 100 == 0:
        reward = 40
    elif clickno % 10 == 0:
        reward = 5

    next_reward = 10
    if clickno % 10 > 0:
        next_reward = 10 - (clickno % 10)
    else:
        next_reward = 10

    if player['score'] > 0 and reward > 0:
        collection = db.players
        player = collection.find_one_and_update({'id': player_id}, {'$inc': {'score': reward}}, return_document=ReturnDocument.AFTER)

    return jsonify(score=player['score'], next_reward=next_reward)

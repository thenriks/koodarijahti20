from pymongo import MongoClient
import mongo_cfg


#client = MongoClient()
#db = client.klikkeri
#newuser = {"name": "Tuomas", "id": 1234}
#players = db.players
#players.insert_one(newuser)

client = MongoClient(mongo_cfg.mongo_url)
db = client.get_default_database()
#db = client['klikkeri']
print(db.list_collection_names())
gstate = db['game_state']
gstate.insert_one({"clicks": 0})

import requests
import pymongo
import json

class LoLUpdater:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['lol_profiles']
        self.summoner_collection = self.db['summoners']
        self.match_collection = self.db['matches']
        self.load_secrets()

    def load_secrets(self):
        with open('secrets.json', 'r') as file:
            secrets = json.load(file)
            self.API_KEY = secrets.get('API_KEY', '')
            self.REGION = secrets.get('REGION', '')

    def get_summoner_profile(self, summoner_name):
        url = f'https://{self.REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
        headers = {'X-Riot-Token': self.API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting summoner profile for {summoner_name}: {response.status_code}")
            return None

    def save_summoner_to_mongodb(self, summoner_data):
        result = self.summoner_collection.replace_one({'summoner_id': summoner_data['id']}, summoner_data, upsert=True)
        print(f"Summoner {summoner_data['name']} inserted/updated with ID {summoner_data['id']}")

    def get_match_history(self, summoner_id):
        url = f'https://{self.REGION}.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}?endIndex=10'
        headers = {'X-Riot-Token': self.API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['matches']
        else:
            print(f"Error getting match history for summoner {summoner_id}: {response.status_code}")
            return None

    def save_matches_to_mongodb(self, matches, summoner_id):
        for match in matches:
            match['_summoner_id'] = summoner_id
            result = self.match_collection.replace_one({'gameId': match['gameId']}, match, upsert=True)
            print(f"Match {match['gameId']} inserted/updated for summoner {summoner_id}")

    def update_summoner_profiles(self, summoner_names=None):
        if summoner_names is None:
            summoner_names = []

        if not summoner_names:
            existing_summoner_names = [doc['summoner_name'] for doc in self.summoner_collection.find({}, {'_id': 0, 'summoner_name': 1})]
            summoner_names.extend(existing_summoner_names)

        for summoner_name in summoner_names:
            summoner_profile = self.get_summoner_profile(summoner_name)
            if summoner_profile:
                self.save_summoner_to_mongodb(summoner_profile)

    def update_match_history_for_all_summoners(self):
        summoners = self.summoner_collection.find({}, {'_id': 0, 'id': 1})
        for summoner in summoners:
            match_history = self.get_match_history(summoner['id'])
            if match_history:
                self.save_matches_to_mongodb(match_history, summoner['id'])

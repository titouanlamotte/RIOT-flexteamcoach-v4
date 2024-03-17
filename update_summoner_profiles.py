import json
from lol_updater import LoLUpdater

def read_summoner_names_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        summoner_names = data.get('summoner_names', [])
    return summoner_names

def main():
    # Read summoner names from summoners.json file
    summoner_names = read_summoner_names_from_json('summoners.json')

    # Update summoner profiles
    lol_updater = LoLUpdater()
    lol_updater.update_summoner_profiles(summoner_names)

if __name__ == '__main__':
    main()

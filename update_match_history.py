from lol_updater import LoLUpdater

def main():
    lol_updater = LoLUpdater()
    lol_updater.update_match_history_for_all_summoners()

if __name__ == '__main__':
    main()

import json
import os, sys
sys.path.append('config')
from config import *

def create_settings_file_if_not_exists():
    if not os.path.exists(CONFIG_FILE):
        config_data = {
            "Theme": {
                "theme": "dark"
            },
            "Telegram": {
                "token": "",
                "chatid": ""
            },
            "Discord": {
                "webhook_url": ""
            },
            "Addresses": {
                "START_ADDRESS": "",
                "END_ADDRESS": ""
            },
            "Paths": {
                "CSS_FOLDER": "css",
                "BLOOM_FOLDER": "bloom",
                "IMAGES_FOLDER": "images",
                "WINNER_FOLDER": "#WINNER",
                "GLOBAL_THEME": "global.css",
                "DARK_THEME": "dark.css",
                "LIGHT_THEME": "light.css",
                "WINNER_COMPRESSED": "foundcaddr.txt",
                "WINNER_UNCOMPRESSED": "founduaddr.txt",
                "WINNER_P2SH": "foundp2sh.txt",
                "WINNER_BECH32": "foundbech32.txt",
                "BTC_BF_FILE": "btc.bf",
                "BTC_TXT_FILE": "btc.txt"
            }
        }
        
        with open(CONFIG_FILE, "w") as file:
            json.dump(config_data, file, indent=4)
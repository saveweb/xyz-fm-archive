import json
import threading
import time

import requests
TOKENS_FILE = 'tokens.json'
from util import Singleton


def save_tokens(tokens: dict):
    if 'success' in tokens:
        del(tokens['success'])
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f, indent=4)

def load_tokens(session: requests.Session):
    ''' pass session to session'''
    with open(TOKENS_FILE, 'r') as f:
        tokens = json.load(f)
        session.headers.update(tokens)
        print(tokens)

def do_auth_tokens_refresh(session: requests.Session):
        url = 'https://api.xiaoyuzhoufm.com/app_auth_tokens.refresh'
        r = session.get(url)
        r.raise_for_status()
        session.headers.update({
            'x-jike-access-token': r.headers['x-jike-access-token'],
            'x-jike-refresh-token': r.headers['x-jike-refresh-token'],
        })
        return r.json() # tokens

def tokens_refresh_loop(session: requests.Session, time_interval: int):
    while True:
        tokens = do_auth_tokens_refresh(session=session)
        save_tokens(tokens=tokens)
        time.sleep(time_interval)

# @Singleton
class TokenKeeper(object):
    session: requests.Session = None
    refreshed = 0

    def __init__(self, session: requests.Session):
        if 'x-jike-access-token' not in session.headers:
            load_tokens(session=session)

        self.session = session

    def token_watch_dog(self):
        if self.refreshed == 0:
            self.refreshed = 1
            t = threading.Thread(target=tokens_refresh_loop, args=(self.session, 10), daemon=True)
            t.start()
        else:
            print('Watchdog started...')

    
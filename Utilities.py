import json
import requests
from collections import deque
from urllib.parse import urlparse


def fix_url(string):
    url = urlparse(string)
    if url[0] == "":
        url = urlparse('https://'+url[1])


def get_extension(url):
    extension = ""
    try:
        url = url['href']
        for x in reversed(range(0, len(url))):
            if url[x] != '.':
                extension += url[x]
            else:
                return extension[::-1]
    except:
        return None


def get_JSON_Obj(file):
    try:
        json_str = ""
        with open(file) as fp:
            json_str = json.load(fp)
        return json_str
    except IOError:
        return None
    except OSError:
        return None
    except FileExistsError:
        return None


def get_text_from_web(url):
    try:
        return requests.get(url).text
    except:
        return None


def parse_suffixes(str):
    suffixes = set()
    for x in str.splitlines():
        if x[:2] != "//" and '.' in x:
            for y in reversed(range(0, len(x))):
                if x[y] == '.':
                    suffixes.add(x[(y + 1):len(x)])
                    break
    return suffixes


def get_suffixes(from_web=False):
    config = get_JSON_Obj("config.json")
    if from_web:
        url = config["url_suffixes"]
        return parse_suffixes(get_text_from_web(url))
    else:
        return get_JSON_Obj(config['local_suffixes'])


def update_local_suffixes():
    try:
        config = get_JSON_Obj("config.json")
        suffixes = get_suffixes(from_web=True)
        f = open(config['local_suffixes'], 'w+')
        json.dump(list(suffixes), f)
        print("Update Successful")
    except:
        print("Update Failed")


def get_all_combos(seedlist, length):
    combos = deque()
    combos.extend(seedlist)
    for x in range(0, length - 1):
        for x in range(0, len(combos)):
            current = combos.popleft()
            for x in seedlist:
                combos.append(current + x)
    return list(combos)


def get_all_capitalization(word):
    words = []
    for x in range(0, len((word))):
        for y in range(0, len(word)):
            words.append(word[x:y].upper())

def swap_items(dest,origin,list_):
    if origin == dest or type(list_) is not list:
        return
    temp = list_[origin]
    list_[origin] = list_[dest]
    list_[dest] = temp
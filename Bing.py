import requests, json

MARKETS = {'es-AR', 'en-AU', 'de-AT', 'nl-BE', 'fr-BE', 'pt-BR', 'en-CA', 'fr-CA', 'es-CL', 'da-DK', 'fi-FI', 'fr-FR',
           'de-DE', 'zh-HK', 'en-IN', 'en-ID', 'en-IE', 'it-IT', 'ja-JP', 'ko-KR', 'en-MY', 'es-MX', 'nl-NL', 'en-NZ',
           'no-NO', 'zh-CN', 'pl-PL', 'pt-PT', 'en-PH', 'ru-RU', 'ar-SA', 'en-ZA', 'es-ES', 'sv-SE', 'fr-CH', 'de-CH',
           'zh-TW', 'tr-TR', 'en-GB', 'en-US', 'es-US'}

SAFE_SEARCH_MODES = {'off', 'moderate', 'strict'}

ERROR_CODES = {429: "Rate limit is exceeded.", 403: "Out of call volume quota",
               401: "Access denied due to invalid subscription key"}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Host': 'api.cognitive.microsoft.com',
    'Ocp-Apim-Subscription-Key': ''}

'''
Search

Interfaces with the bing web search API

:param key api key for bing search api
:type string

:param query is what you want to search for
:type string

:param count represents how many results will be returned
:type integer

:param mkt constrains the search to a geographic area
:type string

:param safesearch controls content based on moral objections
:type string

:return is a response object from the request library
:type response object
'''


def search(key, query, count=150, offset=0, mkt='en-US', safesearch='OFF'):
    if type(key) is not str:
        raise ValueError("Key must be a string")
    elif type(query) is not str:
        raise ValueError('Query must be a string')
    elif count < 1 or type(count) is not int:
        raise ValueError("Count must be an integer greater than zero")
    elif offset < 0 or type(offset) is not int:
        raise ValueError("Offset must be an integer greater than or equal to zero")
    elif mkt not in MARKETS or type(mkt) is not str:
        raise ValueError("Mkt must be in the set of markets a string codes specified my microsoft")
    elif safesearch.lower() not in SAFE_SEARCH_MODES:
        return ValueError("Must have a valid safesearch value")
    else:
        HEADERS['Ocp-Apim-Subscription-Key'] = key
        url = 'https://api.cognitive.microsoft.com/bing/v5.0/search?'
        params = {'q': query, 'count': count, 'offset': offset, 'mkt': mkt, 'safesearch': safesearch}
        results = requests.get(url, params=params, headers=HEADERS)
        return results


def extract_web_links(resp_text):
    resp_json = json.loads(resp_text)
    webpages = resp_json['webPages']['value']
    links = set()
    for x in webpages:
        if 'url' in x:
            links.add(x['url'])
        if 'deepLinks' in x:
            for y in x['deepLinks']:
                links.add(y['url'])
    return links

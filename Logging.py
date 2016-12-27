import Utilities,json
from time import strftime, localtime
from urllib.parse import ParseResult,urlunparse


class Logging:
    file = None

    def __init__(self):
        config = Utilities.get_JSON_Obj('config.json')
        file = open(config['log'], 'a')

    def log(self,form,params,base_url,submit_url,status):
        log_entry = dict()
        log_entry['run_time'] = strftime("%a, %d %b %Y %H:%M:%S", localtime())
        if type(status) is str:
            log_entry['status'] = status
        if type(base_url) is ParseResult:
            log_entry['base_url'] = urlunparse(base_url)
        elif type(base_url) is str:
            log_entry['base_url'] = base_url
        if type(base_url) is ParseResult:
            log_entry['submit_url'] = urlunparse(submit_url)
        elif type(base_url) is str:
            log_entry['submit_url'] = submit_url
        if type(form) is str:
            log_entry['form'] = json.JSONDecoder().decode(form)
        elif type(form) is dict:
            log_entry['form'] = form
        if type(params) is str:
            log_entry['params'] = params
        elif type(params) is dict:
            log_entry['params'] = json.JSONDecoder().decode(params)
        self.file.write(json.JSONEncoder().encode(log_entry))



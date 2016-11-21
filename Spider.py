import requests, Bing
from bs4 import BeautifulSoup
import Utilities
from urllib.parse import urlparse, urlunparse
import requests.exceptions as req_exceptions
import traceback
from time import strftime,localtime
NAME = ['name', 'Name', 'NAME', 'NAme', 'NAMe']
ID = ['ID', 'id', 'Id', 'iD']
FOR = ['FOR', 'For', 'for', 'fOr']
NAME_ID = list()
NAME_ID.extend(ID)
NAME_ID.extend(NAME)
LASTNAME = ['lname', 'lastname', 'l_name', "last_name"]
FIRSTNAME = ['firstname', 'first', 'fname', 'first_name', 'f_name']
EMAIL = ['email']
PHONE = ['phone']


def spider_pig(start, demographics_url):
    print("Started SirSpamAlot on "+strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    config = Utilities.get_JSON_Obj('config.json')
    results = Bing.search(config['bing_api_key'], start)
    to_visit = list()
    to_visit.extend(Bing.extract_web_links(results.text))
    visited = set()
    demographics = Utilities.get_JSON_Obj(demographics_url)
    requests_made = 0
    resp = None
    for x in to_visit:
        if x not in visited:
            base_url_obj = urlparse(x)
            visited.add(x)
            to_visit.remove(x)

            try:
                resp = requests.get(x)
                html = resp.text
                resp.close()
                new_links = extract_links(html, visited, base_url_obj)
                forms = extract_email_forms(html)
                if new_links is not None:
                    to_visit.extend(new_links)
                if forms is not None:
                    execute_forms(forms, base_url_obj, demographics)
                else:
                    continue
            except req_exceptions.RequestException:
                resp.close()
                traceback.print_stack()
            finally:
                requests_made += 1
                print("Requests Made: " + str(requests_made), end="\r")
        else:
            continue

    print("SirSpamAlot was stopped at " + strftime("%a, %d %b %Y %H:%M:%S", localtime()))


'''
extract_links


'''


def extract_links(html, visited_links, base_url):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all(['link', 'a'])
        return sanitize_links(results, visited_links, base_url)
    except:
        return None


def sanitize_links(links, visited_links, base_url):
    goodLinks = []
    extensions = Utilities.get_JSON_Obj("excludeExtensions.json")["ext"]
    for link in links:
        extension = Utilities.get_extension(link)
        if extension not in extensions and link not in visited_links:
            link_obj = urlparse(link['href'])
            if link_obj[0] != "" and link_obj[1] != "":
                goodLinks.append(urlunparse(link_obj))
            else:
                goodLinks.append(base_url.scheme + "://" + base_url.netloc + link['href'])
    return goodLinks


def extract_email_forms(html):
    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")
    email_forms = []
    for x in forms:
        if is_email_form(x):
            email_forms.append(x)
    return email_forms


def execute_forms(forms, base_url_obj, demographics):
    for x in forms:
        result = execute(x, base_url_obj, demographics)
        if result is None:
            print("FORM FAILED TO SUBMIT:\nurl:" + urlunparse(base_url_obj))
            print_form(x)


def print_form(form):
    pass


def execute(form, base_url_obj, demographics):
    method = determine_http_method(form)
    action = get_action(form)
    params = form_to_dictionary(form, demographics)
    url = ""
    if action == '':
        url = urlunparse(base_url_obj)
    else:
        url = base_url_obj[0] + "://" + base_url_obj[1] + action  # makes a base url then places the action at the end
    try:
        result =  requests.get(url, params=params).status_code if method == 'GET' else \
            requests.post(url, data=params).status_code
        return result
    except req_exceptions.RequestException:
        traceback.print_stack()
        return None


def get_action(form):
    if 'action' in form.attrs.keys():
        return form['action']
    else:
        return ""


def determine_http_method(form):
    if 'method' not in form.attrs.keys() or form['method'].upper() == 'GET':
        return 'GET'
    else:
        return 'POST'


'''

recursively checks all the labels in a form to determine if there is a mention of an email form field. If there is
it can be sent off to be executed
'''


def is_email_by_input_tag(input_tags_list):
    if len(input_tags_list) < 1 or input_tags_list is None:
        return False
    lookup = ""
    for x in NAME_ID:
        if x in input_tags_list[0].attrs.keys():
            lookup = x
    if lookup != "" and 'email' in input_tags_list[0][lookup].strip().lower():
        return True
    else:
        return is_email_by_input_tag(input_tags_list[1:])


def is_email_form(form):
    inputs = form.find_all("input")
    if is_email_by_input_tag(inputs):
        return True


'''
according to stack overflow http://stackoverflow.com/questions/7470268/html-input-name-vs-id
name attributes are what are transmitted to the server...
'''


def form_to_dictionary(form, demographics):
    if demographics is None or form is None:
        return None
    form_inputs = form.find_all('input')
    form_dictionary = {}
    for form_input in form_inputs:
        # only an o(n) op the first time around hopefully b/c of the swap
        # hopefully webdevs are somewhat consistent so the second for loop only executes once
        for name in NAME:
            Utilities.swap_items(0, NAME.index(name), NAME)
            if name in form_input.attrs.keys():  # finding how they spell name attribute
                attr = form_input[name]
                attr_type = None
                if 'type' in form_input.attrs.keys():
                    attr_type = form_input['type']
                if attr_type is not None:
                    known_field_log(attr_type, attr, form_input, form_dictionary, demographics)
                else:
                    unknown_field_logic(attr, form_dictionary, demographics)
    return form_dictionary


def known_field_log(attr_type, attr, input_obj, form_dictionary, demographics):
    if attr_type == 'tel':
        form_dictionary[attr] = demographics['phone']
    elif attr_type == 'email':
        form_dictionary[attr] = demographics['email']
    elif attr_type == 'hidden':
        form_dictionary[attr] = input_obj['value']
    elif attr_type == 'password':
        form_dictionary[attr] = demographics['password']
    elif attr_type == 'text':
        unknown_field_logic(attr, form_dictionary, demographics)


def unknown_field_logic(name_attr_value, form_dictionary, demographics):
    if is_attribute(name_attr_value, EMAIL):
        form_dictionary[name_attr_value] = demographics['email']
    elif is_attribute(name_attr_value, FIRSTNAME):
        form_dictionary[name_attr_value] = demographics['first']
    elif is_attribute(name_attr_value, LASTNAME):
        form_dictionary[name_attr_value] = demographics['last']
    elif is_attribute(name_attr_value, PHONE):
        form_dictionary[name_attr_value] = demographics['phone']
    else:
        form_dictionary[name_attr_value] = "call me beautiful and order me a dildo"


def is_attribute(string, GUESS_LIST):
    for x in GUESS_LIST:
        if x in string.lower():
            return True
    return False

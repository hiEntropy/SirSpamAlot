import traceback
import requests
import json
from bs4 import BeautifulSoup
import Utilities
import requests.exceptions as req_exceptions
from urllib.parse import urlunparse, urlparse

NAME_LIST = ['name', 'Name', 'NAME', 'NAme', 'NAMe']
ID = ['ID', 'id', 'Id', 'iD']
FOR = ['FOR', 'For', 'for', 'fOr']
NAME_ID = list()
NAME_ID.extend(ID)
NAME_ID.extend(NAME_LIST)
LASTNAME = ['lname', 'lastname', 'l_name', "last_name"]
FIRSTNAME = ['firstname', 'first', 'fname', 'first_name', 'f_name']
EMAIL = ['email']
PHONE = ['phone']
EXTENSIONS = Utilities.get_JSON_Obj("excludeExtensions.json")["ext"]

'''
extract_email

:param soup is the BeautifulSoup representation of an html page
:type BeautifulSoup Object

:returns None on failure
:returns An empty list when nothing was found
:returns a populated list when something was found
:type list of form objects
'''


def extract_email_forms(soup):
    try:
        forms = soup.find_all("form")
        email_forms = []
        for x in forms:
            if get_interesting_forms(x):
                email_forms.append(x)
        return email_forms
    except:
        traceback.print_stack()
        return None


'''
execute_forms

:param forms to be executed
:type list of BeautifulSoupForms

:base_url_obj is a ParseResult object returned from urllib.parse's urlparse function
:type ParseResult Object

:param demographics represents all the demographics information of the target
:type json object returned from json.load function

:return number of forms submitted
:type int
'''


def execute_forms(forms, base_url_obj, demographics):
    count = 0
    for x in forms:
        result = submit_form(x, base_url_obj, demographics)
        if result is None:
            print("FORM FAILED TO SUBMIT:\nurl:" + urlunparse(base_url_obj))
            form_to_json(x)
        else:
            count += 1
    return count



def form_to_dictionary(form):
    form_dictionary = form.attrs.copy()
    inputs = form.find_all('input')
    form_dictionary['inputs'] = list()
    for input in inputs:
        form_dictionary['inputs'].append(input.attrs.copy())
    return form_dictionary


def form_to_json(form):
    return json.JSONEncoder().encode(form_to_dictionary(form))


def form_to_string(form):
    string = str(form_to_json(form))
    return string


'''
execute

This function is responsible for the form sending logic. Only handles POST and GET request
types. There are a few forms out there that use other methods but they are far and few
in between. Most forms that SirSpamAlot would be interested in would be of the POST and
GET varieties

:param form
:type BeautifulSoup form object

:base_url a ParseResult object returned from urllib.parse's urlparse function
:type ParseResult Object

:param demographics represents all the demographics information of the target
:type json object returned from json.load function

'''


def submit_form(form, base_url_obj, demographics):
    method = determine_http_method(form)
    action = get_action(form)
    params = fillin_form(form, demographics)

    url = ""
    if action is None:
        url = urlunparse(base_url_obj)
    elif action[0] is not "":
        url = urlunparse(action)
    else:
        url = base_url_obj[0] + "://" + base_url_obj[1] + action
        # dealing with relative links and links not to the current url
    try:
        result = requests.get(url, params=params).status_code if method == 'GET' else \
            requests.post(url, data=params).status_code
        return result
    except req_exceptions.RequestException:
        traceback.print_stack()
        return None


def get_action(form):
    if 'action' in form.attrs.keys():
        return urlparse(form['action'])
    else:
        return None


def determine_http_method(form):
    if 'method' not in form.attrs.keys() or form['method'].upper() == 'GET':
        return 'GET'
    else:
        return 'POST'


'''
is_email_form

Looks through different types of tags to determine whether or not they are forms that
SirSpamAlot is interested in.

:param form
:type BeautifulSoup Form Object

:returns True
:returns False
'''


def get_interesting_forms(form):
    inputs = form.find_all("input")
    if is_email_by_input_tag(inputs):
        return True
    return False


'''
fillin_form

The job of this function is to convert html forms into the requests that they represent.
Fields are discovered and populated with demographics data so that a requests.get or request.post
request can be made later.
:reference according to stack overflow http://stackoverflow.com/questions/7470268/html-input-name-vs-id name attributes
           are what are transmitted to the server...

:param form is a form object from BeautifulSoup that converted to a dictionary with populated
       values
:type Beautiful Soup form object

:param demographics represents all the demographics information of the target
:type json object returned from json.load function

:returns
:type dictionary
'''


def fillin_form(form, demographics):
    if demographics is None or form is None:
        return None
    form_inputs = form.find_all('input')
    form_dictionary = {}
    for form_input in form_inputs:
        # only an o(n) op the first time around hopefully b/c of the swap
        # hopefully webdevs are somewhat consistent so the second for loop only executes once
        for name in NAME_LIST:
            Utilities.swap_items(0, NAME_LIST.index(name), NAME_LIST)
            if name in form_input.attrs.keys():  # finding how they spell name attribute
                attr = form_input[name]
                attr_type = None
                if 'type' in form_input.attrs.keys():
                    attr_type = form_input['type']
                if attr_type is not None:
                    known_field_logic(attr_type, attr, form_input, form_dictionary, demographics)
                else:
                    unknown_field_logic(attr, form_dictionary, demographics)
    return form_dictionary


'''
known_field_logic

Uses type attribute data in input tags to fill in data in the parameters dictionary.
So if the type is a tel than it is known that the form wants this attribute to contain a telephone number.

:param attr_type
:type String

:param attr_name
:type String

:param input_obj
:type BeautifulSoup input tag object

:param form_dictionary
:type dictionary

:param demographics
:type json object
'''


def known_field_logic(attr_type, attr_name, input_obj, form_dictionary, demographics):
    if attr_type == 'tel':
        form_dictionary[attr_name] = demographics['phone']
    elif attr_type == 'email':
        form_dictionary[attr_name] = demographics['email']
    elif attr_type == 'hidden':
        if 'value' in input_obj.attrs.keys():
            form_dictionary[attr_name] = input_obj['value']
        else:
            form_dictionary[attr_name] = ""
    elif attr_type == 'password':
        form_dictionary[attr_name] = demographics['password']
    elif attr_type == 'text':
        unknown_field_logic(attr_name, form_dictionary, demographics)


'''
unknown_field_logic

This is used when there is no type attribute. If there is no type attribute the intent of the
web dev must be guessed.

:param attr_name
:string

:param form_dictionary
:type dictionary

:param demographics
:type json object

:returns None
'''


def unknown_field_logic(attr_name, form_dictionary, demographics):
    if is_attribute(attr_name, EMAIL):
        form_dictionary[attr_name] = demographics['email']
    elif is_attribute(attr_name, FIRSTNAME):
        form_dictionary[attr_name] = demographics['first']
    elif is_attribute(attr_name, LASTNAME):
        form_dictionary[attr_name] = demographics['last']
    elif is_attribute(attr_name, PHONE):
        form_dictionary[attr_name] = demographics['phone']
    else:
        form_dictionary[attr_name] = "call me beautiful and order me a pizza"


'''
is_attribute

This is the generalized logic for guessing what type of input tag the program is dealing with
is_attribute is dependent on a list of guesses being passed to it from the calling function

:param attr_name
:type string

:param GUESS_LIST
:type list

:returns True on success
:returns False if there was no match
'''


def is_attribute(attr_name, GUESS_LIST):
    for x in GUESS_LIST:
        if x in attr_name.lower():
            return True
    return False


'''

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

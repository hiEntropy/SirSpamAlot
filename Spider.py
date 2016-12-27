import requests, Bing, Utilities,traceback,Form_Utils
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
import requests.exceptions as req_exceptions
from time import strftime, localtime

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
spider_pig

spider_pig is the main logic loop of SirSpamAlot. This is essentially a breath-first
search of the internet using Bing Search API results as seed data. As forms are found
in html SirSpamAlot attempts to determine what the form is and submit the form with the
targets data. Hopefully this will result in many many web forms being submitted on behalf
of the target resulting in a flood of unsolicited calls and emails.

:param start is a string that is a starting search for Bing.py which wraps the Bing Search API
:type String

:param demographics_url is a path to the demographics information of the target in .json form
:type string

:return void
'''


def spider_pig(start, demographics_url):
    print("Started SirSpamAlot on " + strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    config = Utilities.get_JSON_Obj('config.json')
    results = Bing.search(config['bing_api_key'], start)
    if results is None:
        print("No seed links where acquired")
        return
    to_visit = list()
    to_visit.extend(Bing.extract_web_links(results.text))
    visited = set()
    demographics = Utilities.get_JSON_Obj(demographics_url)
    requests_made = 0
    forms_executed = 0
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
                soup = BeautifulSoup(html, 'html.parser')
                new_links = extract_links(soup, visited, base_url_obj)
                forms = Form_Utils.extract_email_forms(soup)
                if new_links is not None:
                    to_visit.extend(new_links)
                if forms is not None:
                    forms_executed += Form_Utils.execute_forms(forms, base_url_obj, demographics)
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

:param soup BeautifulSoup object representing the html page
:type BeautifulSoup Object

:param visited_links is a set of links that have been visited
:set

:base_url a ParseResult object returned from urllib.parse's urlparse function
:type ParseResult Object

:returns all new links that we have not visited before.
:type list of strings representing urls
'''


def extract_links(soup, visited_links, base_url):
    try:
        results = soup.find_all(['link', 'a'])
        return sanitize_links(results, visited_links, base_url)
    except:
        return None


'''
sanitize_links

:param links are the new links discovered by extract_links
:list of links from BeautifulSoup

:param visited_links is a set of all the links spider_pig has already visited
:set

:base_url a ParseResult object returned from urllib.parse's urlparse function
:type ParseResult Object

:returns the links that are in links but not in visted_links
:type list

'''


def sanitize_links(links, visited_links, base_url):
    good_links = []
    for link in links:
        extension = Utilities.get_extension(link)
        if extension not in EXTENSIONS and link not in visited_links:
            link_obj = urlparse(link['href'])
            if link_obj[0] != "" and link_obj[1] != "":
                good_links.append(urlunparse(link_obj))
            else:
                good_links.append(base_url.scheme + "://" + base_url.netloc + link['href'])
    return good_links








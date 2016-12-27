import unittest
import requests
import Spider, Form_Utils
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import Utilities


class Form_Util_Tests(unittest.TestCase):
    def test_link_extraction(self):
        resp = requests.get("https://docs.python.org/2/library/os.path.html")
        soup = BeautifulSoup(resp.text,'html.parser')
        links = Spider.extract_links(soup, [], urlparse("https://docs.python.org/2/library/os.path.html"))
        self.assertTrue(len(links) > 50)

    def test_sanitize_links(self):
        resp = requests.get("https://docs.python.org/2/library/os.path.html")
        url = urlparse("https://docs.python.org/2/library/os.path.html")
        soup = BeautifulSoup(resp.text,'html.parser')
        links = Spider.extract_links(soup, [], url)
        self.assertTrue(len(links) > 0)

    def test_extract_forms(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        forms = Form_Utils.extract_email_forms(BeautifulSoup(html,'html.parser'))
        self.assertEquals(1, len(forms))


    def test_is_email_by_input_attrs_Coop(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        labels = soup.find_all("input")
        result = Form_Utils.is_email_by_input_tag(labels)
        self.assertEquals(result, True)


    def test_is_email_by_input_attrs_Signup(self):
        html = ""
        with open("Test_Files/SignUpDotCom.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        labels = soup.find_all("input")
        result = Form_Utils.is_email_by_input_tag(labels)
        self.assertEquals(result, True)

    def test_form_to_dictionary(self):
        html = ""
        with open("Test_Files/SignUpDotCom.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        form = soup.find_all("form")
        dem = Utilities.get_JSON_Obj('Test_Files/demographics.json')
        result = Form_Utils.fillin_form(form[0], dem)
        self.assertTrue('email' in result.keys())
        self.assertTrue('firstName' in result.keys())
        self.assertTrue('password' in result.keys())
        self.assertTrue('lastName' in result.keys())

    def test_get_form_method_no_method(self):
        html = ""
        with open("Test_Files/SignUpDotCom.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        form = soup.find_all("form")
        action = Form_Utils.determine_http_method(form[0])
        self.assertEquals("GET",action)

    def test_get_form_method_post(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        form = soup.find_all("form")
        action = Form_Utils.determine_http_method(form[0])
        self.assertEquals("POST", action)

    def test_form_to_dictionary(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        form = soup.find_all("form")
        action = Form_Utils.form_to_dictionary(form[0])
        self.assertEquals(action['method'],'post')
        self.assertEquals(len(action['inputs']), 3)


if __name__ == '__main__':
    unittest.main()

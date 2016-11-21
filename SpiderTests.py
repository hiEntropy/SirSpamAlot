import unittest
import requests
import Spider
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import Utilities


class SpiderTests(unittest.TestCase):
    def test_something(self):
        resp = requests.get("https://docs.python.org/2/library/os.path.html")
        links = Spider.extract_links(resp.text, [], urlparse("https://docs.python.org/2/library/os.path.html"))
        self.assertTrue(len(links) > 50)

    def test_sanitize_links(self):
        resp = requests.get("https://docs.python.org/2/library/os.path.html")
        url = urlparse("https://docs.python.org/2/library/os.path.html")
        links = Spider.extract_links(resp.text, [], url)
        self.assertTrue(len(links) > 0)

    def test_extract_forms(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        forms = Spider.extract_email_forms(html)
        self.assertEquals(1, len(forms))

    def test_is_email_by_label_attrs_Coop(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        labels = soup.find_all("label")
        result = Spider.is_email_by_label_attrs(labels)
        self.assertEquals(result, True)

    def test_is_email_by_input_attrs_Coop(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        labels = soup.find_all("input")
        result = Spider.is_email_by_input_tag(labels)
        self.assertEquals(result, True)

    def test_is_email_by_label_attrs_Signup(self):
        html = ""
        with open("Test_Files/SignUpDotCom.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        labels = soup.find_all("label")
        result = Spider.is_email_by_label_attrs(labels)
        self.assertEquals(result, True)

    def test_is_email_by_input_attrs_Signup(self):
        html = ""
        with open("Test_Files/SignUpDotCom.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        labels = soup.find_all("input")
        result = Spider.is_email_by_input_tag(labels)
        self.assertEquals(result, True)

    def test_form_to_dictionary(self):
        html = ""
        with open("Test_Files/SignUpDotCom.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        form = soup.find_all("form")
        dem = Utilities.get_JSON_Obj('Test_Files/demographics.json')
        result = Spider.form_to_dictionary(form[0], dem)
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
        action = Spider.determine_http_method(form)
        self.assertEquals("GET",action)

    def test_get_form_method_no_method(self):
        html = ""
        with open("Test_Files/CoOpSubscribeForm.html", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        form = soup.find_all("form")
        action = Spider.determine_http_method(form)
        self.assertEquals("POST", action)


if __name__ == '__main__':
    unittest.main()

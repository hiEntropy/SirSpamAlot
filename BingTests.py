import unittest
import Bing
import Utilities


class BingTests(unittest.TestCase):
    key = ""
    text = ""

    def setUp(self):
        configs = Utilities.get_JSON_Obj('config.json')
        self.key = configs['bing_api_key']
        with open('Test_Files/bing_api_resp_2.json','r',errors='ignore') as f:
            self.text = f.read()

    def test_basic_request(self):
        query = 'seahawks'
        response = Bing.search(self.key,query)
        self.assertEqual(response.status_code, 200)

    def test_link_extraction(self):
        results = Bing.extract_web_links(self.text)
        self.assertTrue(len(results)>6)


if __name__ == '__main__':
    unittest.main()

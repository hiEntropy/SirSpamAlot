import unittest
import Utilities


class UtilTests(unittest.TestCase):
    def test_parse_suffixes(self):
        file = ""
        with open("suffixes_raw_test.txt",errors="ignore") as f:
            file = f.read()
        suffixes = Utilities.parse_suffixes(file)
        self.assertTrue('org' in suffixes)
        self.assertTrue('com' in suffixes)
        self.assertTrue('ae' in suffixes)
        self.assertTrue('jp' in suffixes)
        self.assertTrue('ma' in suffixes)
        self.assertTrue('me' in suffixes)
        self.assertTrue('us' in suffixes)
        self.assertTrue('to' in suffixes)
    def test_parse_suffixes_from_web(self):
        text = Utilities.get_text_from_web("http://publicsuffix.org/list/public_suffix_list.dat")
        suffixes = Utilities.parse_suffixes(text)
        self.assertTrue('org' in suffixes)
        self.assertTrue('com' in suffixes)
        self.assertTrue('ae' in suffixes)
        self.assertTrue('jp' in suffixes)
        self.assertTrue('ma' in suffixes)
        self.assertTrue('me' in suffixes)
        self.assertTrue('us' in suffixes)
        self.assertTrue('to' in suffixes)

    def test_local_suffixes(self):
        Utilities.update_local_suffixes()


if __name__ == '__main__':
    unittest.main()

import unittest
import subprocess
import logging
import evaluate
import argparse

class TestRepositories(unittest.TestCase):
    logger : logging.Logger = None  

    def TestRepositories(self):
        self.logger = logging.getLogger()
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    def setUp(self) -> None:
        evaluate.setup_args()
        evaluate.args = evaluate.parser.parse_args()

    def tearDown(self) -> None:
        evaluate.args = argparse.Namespace()
    
    def fetch_repository(self, repo_url : str):
        evaluate.args.project = repo_url 
        evaluate.run(True)

    def test_unsafer_repository_git(self):
        """
        Tests unsafer repository with GitHub Link
        """
        self.fetch_repository("https://github.com/stg-tud/go-safer.git")


if __name__ == '__main__':
    unittest.main()
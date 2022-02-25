import unittest
import subprocess
import logging
import evaluate
import argparse
import json 

class TestRepositories(unittest.TestCase):
    logger : logging.Logger = None  

    def TestRepositories(self):
        self.logger = logging.getLogger()
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    def setUp(self) -> None:
        evaluate.setup_args()
        evaluate.args, _ = evaluate.parser.parse_known_args()

    def tearDown(self) -> None:
        evaluate.args = argparse.Namespace()
    
    def evaluate_on_repository(self, repo_url : str):
        evaluate.args.project = repo_url 
        return evaluate.run()
    
    def run_on_repository(self, repo_url : str):
        subprocess.run(args = f"python3 run.py -p {repo_url}", check = True, shell = True)
        with json.load("./output/output.json") as output_dic:
            return output_dic

    def test_unsafer_repository_git(self):
        """
        Tests unsafer repository with GitHub Link
        """
        output_dic = self.evaluate_on_repository("https://github.com/stg-tud/go-safer.git")
        self.assertGreater(len(output_dic.items()), 0)
    
    def test_unsafer_repository_git_ssh(self):
            """
            Tests unsafer repository with GitHub Link
            """
            output_dic = self.evaluate_on_repository("git@github.com:stg-tud/go-safer.git")
            self.assertGreater(len(output_dic.items()), 0)

    def test_grpc_repository_git_ssh(self):
        """
        Tests unsafer repository with GitHub Link
        """
        output_dic = self.evaluate_on_repository("git@github.com:grpc/grpc-go.git")
        self.assertGreater(len(output_dic.items()), 0)

    def test_unsafer_repository_git_runner(self):
        """
        Tests unsafer repository with GitHub Link
        """
        output_dic = self.run_on_repository("https://github.com/stg-tud/go-safer.git")
        self.assertGreater(len(output_dic.items()), 0)

if __name__ == '__main__':
    unittest.main()
import unittest
import subprocess
import logging
import evaluate
import argparse
import json 
import tempfile
import os

class TestRepositories(unittest.TestCase):
    logger : logging.Logger = None  
    go_path : str = None 

    @classmethod
    def setUpClass(self):
        self.logger = logging.getLogger()
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        self.go_path = os.environ["GOPATH"]

    def setUp(self) -> None:
        evaluate.setup_args()
        evaluate.args, _ = evaluate.parser.parse_known_args()

    def tearDown(self) -> None:
        evaluate.args = argparse.Namespace()
    
    def evaluate_on_repository(self, repo_url : str):
        evaluate.args.project = repo_url 
        return evaluate.run()
    
    def clone_repository(self, repo_url : str):
        modified_env = os.environ.copy()
        modified_env["GIT_TERMINAL_PROMPT"] = "0"
        temp_dir = tempfile.mkdtemp() + '/'
        self.logger.info(f"Running git clone on {repo_url}")
        process = subprocess.run(args=["git", "clone", "--depth", "1" , repo_url], capture_output=True, check=True, env=modified_env, cwd=temp_dir)
        return temp_dir + repo_url.split('/')[-1].replace('.git', '')

    def run_on_repository(self, repo_url : str):
        try:
            process = subprocess.run(args = f"python3 run.py -p {repo_url}", check = True, shell = True, capture_output = True)
            with open("./output/output.json") as f:
                return json.load(f)
        except subprocess.CalledProcessError as e:
            self.logger.error(e.stdout)
            self.logger.error(e.stderr)
            raise e
        
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
        evaluate.args.concurrent_threads = 1
        self.assertGreater(len(output_dic.items()), 0)

    def test_unsafer_repository_git_ssh_concurrent(self):
        """
        Tests unsafer repository with GitHub Link
        """
        output_dic = self.evaluate_on_repository("git@github.com:stg-tud/go-safer.git")
        evaluate.args.concurrent_threads = 6
        self.assertGreater(len(output_dic.items()), 0)

    @unittest.skip("Large test")
    def test_grpc_repository_git_ssh(self):
        """
        Tests unsafer repository with GitHub Link
        """
        self.logger.warn("This is a large repository. Expect the test to take a longe time and 400+ lines to analyze.")
        evaluate.args.concurrent_threads = 1
        output_dic = self.evaluate_on_repository("git@github.com:grpc/grpc-go.git")
        self.assertGreater(len(output_dic.items()), 0)

    @unittest.skip("Large test")
    def test_grpc_repository_git_ssh_concurrent(self):
        """
        Tests unsafer repository with GitHub Link
        """
        self.logger.warn("This is a large repository. Expect the test to take a longe time and 400+ lines to analyze.")
        evaluate.args.concurrent_threads = 6
        output_dic = self.evaluate_on_repository("git@github.com:grpc/grpc-go.git")
        self.assertGreater(len(output_dic.items()), 0)

    def test_unsafer_repository_git_runner(self):
        """
        Tests unsafer repository with GitHub Link
        """
        output_dic = self.run_on_repository("https://github.com/stg-tud/go-safer.git")
        self.assertGreater(len(output_dic.items()), 0)

    def test_unsafer_repository_local_runner(self):
        """
        Tests local unsafer repository with GitHub Link
        """
        temp_dir = self.clone_repository("https://github.com/stg-tud/go-safer.git")
        output_dic = self.run_on_repository(temp_dir)
        self.assertGreater(len(output_dic.items()), 0)

    def test_unsafer_repository_local(self):
        """
        Tests local unsafer repository with GitHub Link
        """
        temp_dir = self.clone_repository("https://github.com/stg-tud/go-safer.git")
        output_dic = self.evaluate_on_repository(temp_dir)
        self.assertGreater(len(output_dic.items()), 0)

    def test_gitlabshell_repository_local(self):
        """
        Tests Gitlab Shell which contains several go.mod 
        """
        output_dic = self.evaluate_on_repository("https://gitlab.com/gitlab-org/gitlab-shell.git")
        self.assertGreater(len(output_dic.items()), 0)

    def test_gitlabshell_repository_runner(self):
        """
        Tests Gitlab Shell which contains several go.mod 
        """
        output_dic = self.run_on_repository("https://gitlab.com/gitlab-org/gitlab-shell.git")
        self.assertGreater(len(output_dic.items()), 0)

class TestFunctions(unittest.TestCase):
    logger : logging.Logger = None  
    go_path : str = None 

    @classmethod
    def setUpClass(self):
        self.logger = logging.getLogger()
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        self.go_path = os.environ["GOPATH"]

    def test_get_package_name(self):
        package_name = evaluate.get_package_name(f"{self.go_path}/pkg/mod/github.com/rs/xid@v1.3.0/id.go")
        self.assertEqual(package_name ,"github.com/rs/xid")
    
    def test_get_package_name_2(self):
        package_name = evaluate.get_package_name(f"{self.go_path}/pkg/mod/google.golang.org/protobuf@v1.25.0/internal/strs/strings_unsafe.go")
        self.assertEqual(package_name ,"google.golang.org/protobuf/internal/strs") 

    def test_get_package_name_3(self):
        package_name = evaluate.get_package_name(f"{self.go_path}/pkg/mod/github.com/rs/zerolog@v1.26.2-0.20220227173336-263b0bde3672/fields.go")
        self.assertEqual(package_name ,"github.com/rs/zerolog") 

    def test_get_forked_package_name(self):
        package_name = evaluate.get_package_name(f"{self.go_path}/pkg/mod/github.com/drakkan/crypto@v0.0.0-20220215181150-74469fa99b22/internal/subtle/aliasing.go")
        self.assertEqual(package_name ,"golang.org/x/crypto/internal/subtle") 
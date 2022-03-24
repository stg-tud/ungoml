#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

from importlib.util import module_for_loader
import sys
import os
import json
import subprocess
import argparse
import tempfile
from pygments import highlight, lexers, formatters
from typing import List, Dict, Tuple
from collections import OrderedDict
import regex
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing
import logging

parser : argparse.ArgumentParser = None 
args : argparse.Namespace = None 
projects_dir : str = None 
classifier_path : str = None 
interactive, debug, container_mode  = (False, False, False)
logger : logging.Logger = None
item_count : int = None 

def get_lines(cwd : str = None) -> dict: 
    """ Runs go-geiger on the project argument and fetches the lines with unsafe unsages.

    Returns:
        dict: The dictionary with the line numbers of unsafe usages mapped to the corresponding files.
    """
    try:
        stdout : str = None
        if cwd == None:
            cwd = args.project
        process = subprocess.run(args=["go-geiger", "--show-code", "."], cwd=cwd, capture_output=True, check=True)
        stdout = process.stdout.decode("utf-8")
        logger.debug(stdout)
        output_lines = stdout.split("\n")
        # grep command
        relevant_lines = list(filter( lambda x : "go:" in x , output_lines))
        # Equivalent to tr -f 
        file_line_tuples = list(map(lambda x : x.split(':')[:2], relevant_lines))
        dic = dict()
        for file, line in file_line_tuples:
            # file = file.split('/')[-1]
            if not file in dic.keys() : 
                dic[file] = list()
            dic[file].append(line)
        return dic 
    except subprocess.CalledProcessError as e:
        logger.error(e.stdout.decode("utf-8"))
        logger.error(e.stderr.decode("utf-8"))
        raise(e)

def get_lines_detailed(cwd : str):
    """ 
    Runs go-geiger on the directories containing main.go. Will be called when running go-geiger on the go.mod directory returns no analyzed lines.

    Raises:
        NotImplementedError: _description_
    """
    dic = {}
    for dirpath, dirnames, filenames in os.walk(cwd):
        if "main.go" in filenames:
            dic = {**dic, **get_lines(dirpath)} 
    return dic

def setup_args():
    """
    Adds the arguments for the argument parser
    """
    global parser
    parser = argparse.ArgumentParser()
    # parser.add_argument("-f", "--file", help="File name of Go file to analyze", required=True)
    parser.add_argument( "-p", "--project", help="Path of package where the Go file lies in", default="/project")
    # parser.add_argument("--package", help="Package name of Go file", required = True)
    parser.add_argument("-o", "--output", help="Output file of JSON file", required = False, default = "output/output.json")
    # parser.add_argument("-c", "classifier-path", help="Path of the directory of the classifier", default="../unsafe-go-classifier")
    parser.add_argument("-m", "--mode", help="Mode of output file, choose between the strings readable or machine", required=False, default="machine")
    parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
    # TODO: Add parallel task number
    parser.add_argument("-c", "--concurrent-threads", help="Number of concurrent evaluation containers the script should run", default=multiprocessing.cpu_count())

def setup():
    """
    
    Parses the args and downloads the repository with Git if needed.

    """
    global interactive, debug, container_mode, logger, args
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    if __name__ == "__main__":
        setup_args()
        args, unknown = parser.parse_known_args()
    args.output = os.path.realpath(args.output) 
    interactive = sys.stdout.isatty()
    debug =  os.getenv("DEBUG", 'False').lower() in ('true', '1', 't') or args.debug
    logger = logging.getLogger()
    if debug:
        logger.setLevel("DEBUG")
    else: 
        logger.setLevel("INFO")
    container_mode = os.getenv("CONTAINER_MODE", 'False').lower() in ('true', '1', 't')
    logger.debug(args)
    # if project path ends with git, clone the directory 
    try:
        if not os.path.exists(args.project):
            # disable terminal prompt for git ls-remote
            modified_env = os.environ.copy()
            modified_env["GIT_TERMINAL_PROMPT"] = "0"
            process = subprocess.run(args=["git", "ls-remote", args.project], capture_output=True, check=True, env=modified_env)
            temp_dir = tempfile.mkdtemp() + '/'
            # TODO: Get repository with minimal depth
            logger.info(f"Running git clone on {args.project}")
            process = subprocess.run(args=["git", "clone", "--depth", "1" , args.project], capture_output=True, check=True, env=modified_env, cwd=temp_dir)
            # TODO: go build
            args.project = temp_dir + args.project.split('/')[-1].replace('.git', '')
            # change to cloned directory
        logger.info(f"Running go build on {args.project}:")
        process = subprocess.run(args=["go", "build", "..."], capture_output=True, cwd=args.project)
            
    except subprocess.CalledProcessError as e:
        logger.error(e.stdout.decode("utf-8"))
        logger.error(e.stderr.decode("utf-8"))
        raise(e)
        
def run():
    global item_count
    setup()
    output_dic = {}
    file_lines_dictionary = get_lines()
    if len(file_lines_dictionary.items()) == 0:
        file_lines_dictionary = get_lines_detailed(args.project)
    
    if len(file_lines_dictionary.items()) == 0:
        raise Exception("No lines to classify have been found!")

    # get total item count
    item_count = sum(map(len, file_lines_dictionary.values()))
    if interactive:
        logger.info("Total lines to classify: %d" % (item_count))

    classified_count = 0
    # prepare pool
    pool = Pool(args.concurrent_threads)

    for file_tuple in file_lines_dictionary.items():
        # classified_count = sum(map(len, output_dic.values()))
        # TODO: Parallelize this
        pool.apply_async(evaluate_file, (file_tuple, output_dic))
    
    pool.close()
    pool.join()

    formatted_json = json.dumps(output_dic , indent=4)
    colorful_json = highlight(str.encode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    logger.debug(colorful_json)
    if not os.path.exists(os.path.dirname(args.output)):
        os.mkdir(os.path.dirname(args.output))
    with open(args.output, 'w') as file:
        file.write(formatted_json)

    return output_dic

def evaluate_file(file_tuple : Tuple[str, List[int]], output_dic : Dict):
    file = file_tuple[0]
    lines : List[int] = file_tuple[1]
    
    project_path = get_project_path(file)
    project_name = project_path.split('/')[-1]
    parent_path = os.path.realpath(('/').join(project_path.split('/')[:-1]))
    relative_file_path = file.split('/')[-1]
    file_content : List[str] = None 
    with open(file) as f:
        file_content = f.readlines()
    package = get_package_name(file)
    
    package_file_path = "%s/%s" % (package, relative_file_path)
    output_dic[package_file_path] = dict()
    
    for line in lines:
        # package = file_content[0].replace('package', '').strip()
        docker_args = f'--go-version 1.17 --project {project_name} --line {line} --package {package} --file {relative_file_path} --base {parent_path} predict -m WL2GNN'
        # Run container for each line 
        try:
            parent_mount = f"-v {parent_path}:{parent_path}"
            if container_mode and os.environ["GOPATH"] in parent_mount:
                # Parent mount is unnecessary since the same go_mod volume is loaded 
                parent_mount = ""
            command = f"docker run --rm \
                -v go_mod:/root/go/pkg/mod -v go_cache:/root/.cache/go-build {parent_mount} \
                usgoc/pred:latest {docker_args}" 
            stdout : str = None 
            logger.debug("Running command: %s" % command)
            process = subprocess.run(args = command, capture_output=True, check = True, shell=True)
            stdout = process.stdout.decode("utf-8")
            # print("Line: %s" % line)
            # JSON loads a JSON list 
            evaluate_list = []
            evaluate_list.append(file_content[int(line) - 1].strip())
            logger.debug(stdout)
            for dic in json.loads(stdout):
                if args.mode == "readable":
                    for k, v in dic.items():
                        dic[k] = round(v, 4)
                prediction : OrderedDict = OrderedDict(sorted(
                    dic.items(), key = lambda x : x[1], reverse = True 
                    )) 
                evaluate_list.append(prediction)
            output_dic[package_file_path][line] = evaluate_list
        except subprocess.CalledProcessError as e:
            logger.error(e.args)
            logger.error(e.stdout.decode("utf-8"))
            logger.error(e.stderr.decode("utf-8"))
            raise(e)
    classified_count = sum(map(len, output_dic.values()))
    logger.info(f"Finished running classifier for file: {file_tuple[0]}. Classified lines: {classified_count}/{item_count}")


def get_project_path(file_path : str) -> str:
    """ 
    Gets the project folder path which contains the go.mod file.

    Args:
        file_path (str): Path of a file / folder which is inside the wanted project folder

    Returns:
        str: The project folder path
    """
    path_list = file_path.split('/')
    
    for i in range(1, len(path_list) - 1):
        possible_project_path = '/'.join(path_list[:-i])
        directory = os.listdir(possible_project_path)
        if ( "go.mod" in directory ):
            return possible_project_path

def get_package_name(file_path : str) -> str:
    """
    Get fully qualified package name which is the package name in the .go file prepended by the relative path to the project folder path.

    Args:
        file_path (str): Path to the .go file 

    Returns:
        str: The fully qualified package name
    """
    package_path = None 
    project_path = get_project_path(file_path)
    go_mod_path = project_path + "/go.mod"
    module_name : str = "" 
    if (os.path.isfile(go_mod_path)):
        try: 
        # get package name 
            with open(go_mod_path) as file:
                module_name = list(filter(lambda x : "module" in x, file.readlines()))[0].split()[1]
        except PermissionError as e:
            logger.warn("Could not read go.mod file:", e) 
        except Exception as e:
            logger.fatal(e)
    if ('/go/pkg/' in file_path):
        package_path = file_path.split('/pkg/')[1]
        package_path = ('/').join(package_path.split('/')[1:-1])
        # remove version tag
        # package_path = regex.sub(r'(.+?)(@.+?)(/.+)', r'\1\3', package_path)
        package_path = regex.sub(r'(.+?)(@[^/]+)((?:/).+)?', r'\1\3', package_path)
    else:
        project_path = get_project_path(file_path)
        # last item of splitted project path
        package_path = project_path.split('/')[-1]
    if module_name not in package_path:
        unqualified_module_name = module_name.split('/')[-1]
        # search for unqualified module name in package path
        unqualified_index = package_path.split('/').index(unqualified_module_name)
        # append correct module name with fork package name
        package_path = module_name + '/' + '/'.join(package_path.split('/')[unqualified_index + 1 :])
    return package_path

if __name__ == "__main__":
    run()




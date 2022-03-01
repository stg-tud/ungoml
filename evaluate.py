#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

from code import interact
from contextlib import redirect_stdout
import sys
import os
import json
import subprocess
import argparse
import tempfile
from pygments import highlight, lexers, formatters
from typing import List
from collections import OrderedDict
import regex
import logging

parser : argparse.ArgumentParser = argparse.ArgumentParser()
args : argparse.Namespace = None 
projects_dir : str = None 
classifier_path : str = None 
interactive, debug, container_mode  = (False, False, False)
logger : logging.Logger = None

def get_lines() -> dict: 
    try:
        stdout : str = None
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
    raise NotImplementedError()

def setup_args():
    # parser.add_argument("-f", "--file", help="File name of Go file to analyze", required=True)
    parser.add_argument( "-p", "--project", help="Path of package where the Go file lies in", default="/project")
    # parser.add_argument("--package", help="Package name of Go file", required = True)
    parser.add_argument("-o", "--output", help="Output file of JSON file", required = False, default = "output/output.json")
    # parser.add_argument("-c", "classifier-path", help="Path of the directory of the classifier", default="../unsafe-go-classifier")
    # TODO: Output style, readable, machine etc.
    parser.add_argument("-m", "--mode", help="Mode of output file, choose between the strings readable or machine", required=False, default="machine")
    parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
    

def setup():
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
        
        
    # get real path of project dir
    # args.project = os.path.realpath(args.project)
    # go-geiger gives different results based on relative path and real path 

    classifier_path = None 

def run():
    setup()
    output_dic = {}
    file_lines_dictionary = get_lines()
    
    # get total item count
    item_count = sum(map(len, file_lines_dictionary.values()))
    if interactive:
        logger.info("Total lines to classify: %d" % (item_count))

    classified_count = 0
    # prepare docker args
    for file, lines in file_lines_dictionary.items():
        logger.info(f"Running classifier for file: {file}. Classified lines: {classified_count}/{item_count}")
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
            docker_args = f'--project {project_name} --line {line} --package {package} --file {relative_file_path} --base {parent_path} predict -m WL2GNN'
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
                classified_count += 1
            except subprocess.CalledProcessError as e:
                logger.error(e.args)
                logger.error(e.stdout.decode("utf-8"))
                logger.error(e.stderr.decode("utf-8"))
                raise(e)
        

    formatted_json = json.dumps(output_dic , indent=4)
    colorful_json = highlight(str.encode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    logger.debug(colorful_json)
    if not os.path.exists(os.path.dirname(args.output)):
        os.mkdir(os.path.dirname(args.output))
    with open(args.output, 'w') as file:
        file.write(formatted_json)

    return output_dic


def get_project_path(file_path : str):
    path_list = file_path.split('/')
    
    for i in range(1, len(path_list) - 1):
        possible_project_path = '/'.join(path_list[:-i])
        directory = os.listdir(possible_project_path)
        if ( "go.mod" in directory ):
            return possible_project_path

def get_package_name(file_path : str):
    package_path = None 
    if ('/go/pkg/' in file_path):
        package_path = file_path.split('/pkg/')[1]
        package_path = ('/').join(package_path.split('/')[1:-1])
        # remove version tag
        package_path = regex.sub(r'(.+?)(@.+?)(/.+)', r'\1\3', package_path)
    else:
        project_path = get_project_path(file_path)
        # last item of splitted project path
        package_path = project_path.split('/')[-1]
    return package_path

if __name__ == "__main__":
    run()




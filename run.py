#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

import sys
import os
import json
import subprocess
import argparse
import tempfile
from pygments import highlight, lexers, formatters
from typing import List
from collections import OrderedDict


parser : argparse.ArgumentParser = argparse.ArgumentParser()
args : argparse.Namespace = None 
projects_dir : str = None 
classifier_path : str = None 


def get_lines() -> dict: 
    try:
        stdout : str = None 
        process = subprocess.run(args=["go-geiger", "--show-code", '.'], cwd=args.project, capture_output=True, check=True)
        stdout = process.stdout.decode("utf-8")
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
        print(e.stdout.decode("utf-8"))
        print(e.stderr.decode("utf-8"))
        raise(e)
    raise NotImplementedError()

def parse_args():
    global args
    # parser.add_argument("-f", "--file", help="File name of Go file to analyze", required=True)
    parser.add_argument( "-p", "--project", help="Path of package where the Go file lies in", default="/project")
    # parser.add_argument("--package", help="Package name of Go file", required = True)
    parser.add_argument("-o", "--output", help="Output file of JSON file", required = False, default = "output.json")
    # parser.add_argument("-c", "classifier-path", help="Path of the directory of the classifier", default="../unsafe-go-classifier")
    # TODO: Output style, readable, machine etc.
    parser.add_argument("-m", "--mode", help="Mode of output file, choose between the strings readable or machine", required=False, default="machine")
    args = parser.parse_args()

def setup():
    parse_args()

    # if project path ends with git, clone the directory 
    try:
        if not os.path.exists(args.project):
            # disable terminal prompt for git ls-remote
            modified_env = os.environ.copy()
            modified_env["GIT_TERMINAL_PROMPT"] = "0"
            process = subprocess.run(args=["git", "ls-remote", args.project], capture_output=True, check=True, env=modified_env)
            temp_dir = tempfile.mkdtemp() + '/'
            process = subprocess.run(args=["git", "clone", args.project], capture_output=True, check=True, env=modified_env, cwd=temp_dir)
            # TODO: go build
            args.project = temp_dir + args.project.split('/')[-1].replace('.git', '')
            # change to cloned directory
            print(args.project)
            process = subprocess.run(args=["go", "build", "..."], capture_output=True, cwd=args.project)
            
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode("utf-8"))
        print(e.stderr.decode("utf-8"))
        raise(e)
        
        
    # get real path of project dir
    # args.project = os.path.realpath(args.project)
    # go-geiger gives different results based on relative path and real path 

    classifier_path = None 

def run():
    setup()
    output_dic = {}
    file_lines_dictionary = get_lines()
    
    # prepare docker args
    
    for file, lines in file_lines_dictionary.items():
        parent_path = os.path.realpath(('/').join(file.split('/')[:-2]))
        project_path = file.split('/')[-2]
        relative_file_path = file.split('/')[-1]
        file_content : List[str] = None 
        with open(file) as f:
            file_content = f.readlines()
        package = get_package_name(file_content)
        output_dic[relative_file_path] = dict()
        for line in lines:
            # package = file_content[0].replace('package', '').strip()
            docker_args = f'--project {project_path} --line {line} --package {package} --file {relative_file_path} predict -m WL2GNN'
            # Run container for each line 
            try: 
                command = f"docker run --rm \
                    -v go_mod:/root/go/pkg/mod -v go_cache:/root/.cache/go-build -v {parent_path}:/projects \
                    usgoc/pred:latest {docker_args}" 
                stdout : str = None 
                print("Running command: %s" % command)
                process = subprocess.run(args = command, capture_output=True, check = True, shell=True)
                stdout = process.stdout.decode("utf-8")
                # print("Line: %s" % line)
                # JSON loads a JSON list 
                evaluate_list = []
                evaluate_list.append(file_content[int(line) - 1].strip())
                for dic in json.loads(stdout):
                    prediction : OrderedDict = OrderedDict(sorted(
                        dic.items(), key = lambda x : x[1], reverse = True 
                        )) 
                    evaluate_list.append(prediction)
                output_dic[relative_file_path][line] = evaluate_list
            except subprocess.CalledProcessError as e:
                print(e.stdout.decode("utf-8"))
                print(e.stderr.decode("utf-8"))
                raise(e)
        

    formatted_json = json.dumps(output_dic , indent=4)
    colorful_json = highlight(str.encode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    # TBD
    print(colorful_json)
    with open(args.output, 'w') as file:
        file.write(formatted_json)
    
def get_package_name(file):
    for line in file:
        if "package" in line:
            return line.replace("package ", '').strip()

if __name__ == "__main__":
    run()




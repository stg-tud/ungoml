#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

import sys
import os
import json
import subprocess
import argparse
from pygments import highlight, lexers, formatters
from typing import List
from collections import OrderedDict

parser : argparse.ArgumentParser = argparse.ArgumentParser()
args : argparse.Namespace = None 
projects_dir : str = None 
classifier_path : str = None 


def get_lines() -> dict: 
    try:
        command = f"go-geiger --show-code {args.project}" 
        stdout : str = None 
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True) as process:
            stdout = process.communicate()[0].decode("utf-8")
            # print(stdout)
        # process = subprocess.run(executable="go-geiger", args=["--show-code", args.project], capture_output=True, check=True)
        output_lines = stdout.split("\n")
        # grep command
        relevant_lines = list(filter( lambda x : "go:" in x , output_lines))
        # Equivalent to tr -f 
        file_line_tuples = list(map(lambda x : x.split(':')[:2], relevant_lines))
        dic = dict()
        for file, line in file_line_tuples:
            file = file.split('/')[-1]
            if not file in dic.keys() : 
                dic[file] = list()
            dic[file].append(line)
        return dic 
    except subprocess.CalledProcessError as e:
        print(e)
        sys.exit(-1)
    raise NotImplementedError()

def parse_args():
    global args
    # parser.add_argument("-f", "--file", help="File name of Go file to analyze", required=True)
    parser.add_argument( "-p", "--project", help="Path of package where the Go file lies in")
    parser.add_argument("--package", help="Package name of Go file", required = True)
    parser.add_argument("-o", "--output", help="Output file of JSON file", required = False, default = "output.json")
    # parser.add_argument("-c", "classifier-path", help="Path of the directory of the classifier", default="../unsafe-go-classifier")
    # TODO: Output style, readable, machine etc.
    args = parser.parse_args()

def setup():
    parse_args()
    # get real path of project dir
    # args.project = os.path.realpath(args.project)
    # go-geiger gives different results based on relative path and real path 

    classifier_path = None 

def run():
    setup()
    output_dic = {}
    file_lines_dictionary = get_lines()
    
    # prepare docker args
    project_parent_dir = os.path.realpath('/'.join(args.project.split('/')[:-1]))
    for file, lines in file_lines_dictionary.items():
        output_dic[file] = dict()
        for line in lines:
            docker_args = f'--project {args.project.split("/")[-1]} --line {line} --package {args.package} --file {file} predict -m WL2GNN'
            # Run container for each line 
            try: 
                command = f"docker run --rm \
                    -v go_mod:/root/go/pkg/mod -v go_cache:/root/.cache/go-build -v {project_parent_dir}:/projects \
                    usgoc/pred:latest {docker_args}" 
                stdout : str = None 
                print("Running command: %s" % command)
                with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True) as process:
                    stdout = process.communicate()[0].decode("utf-8")
                    if process.returncode != 0:
                        raise Exception("Exit code from docker run stdout is not 0. Output: %s" % stdout )
                '''
                process = subprocess.run(args = f"run --rm \
                    -v go_mod:/root/go/pkg/mod -v go_cache:/root/.cache/go-build -v {args.project}:/projects \
                    usgoc/pred:latest {docker_args}", executable="docker", capture_output=True, check = True)
                '''
                # print("Line: %s" % line)
                # JSON loads a JSON list 
                evaluate_list = []
                for dic in json.loads(stdout):
                    prediction : OrderedDict = OrderedDict(sorted(
                        dic.items(), key = lambda x : x[1], reverse = True 
                        )) 
                    evaluate_list.append(prediction)
                output_dic[file][line] = evaluate_list
            except Exception as e:
                print(e)
                sys.exit(1)
        

    formatted_json = json.dumps(output_dic , indent=4)
    colorful_json = highlight(str.encode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    # TBD
    print(colorful_json)
    with open(args.output, 'w') as file:
        file.write(formatted_json)
    

if __name__ == "__main__":
    run()




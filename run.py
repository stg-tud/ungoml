#!/usr/bin python3 
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

def get_lines(): 
    try:
        process = subprocess.run(executable="go-geiger", args=f'--show-code --project {args.project}', shell=True, capture_output=True, check=True)
        output_lines = str(process.stdout, "utf-8").split("\n")
        # grep command
        relevant_lines = filter( lambda x : "go:" in x , output_lines)
        # Equivalent to tr -f 
        line_numbers = map(lambda x : x.split(':')[2] )
        return line_numbers
    except subprocess.CalledProcessError as e:
        print(e)
        sys.exit(-1)
    raise NotImplementedError()

def parse_args():
    global args
    parser.add_argument("-f", "file", help="File name of Go file to analyze", required=True)
    parser.add_argument("-p", "project", help="Path of package where the Go file lies in", default=os.environ["PROJECTS_DIR"])
    args = parser.parse_args()

def setup():
    parse_args()
    classifier_path = None 

def run():
    setup()
    lines = get_lines()
    for line in lines:
        # Run container for each line 
        process = subprocess.run(args = "--rm $ARGS \
            -v go_mod:/root/go/pkg/mod -v go_cache:/root/.cache/go-build -v $pd:/projects \
            usgoc/pred:latest $@", executable="docker", capture_output=True)

        prediction : OrderedDict = OrderedDict(sorted(
            json.loads(process.stdout).items(), key = lambda x : x[1], reversed = True 
            )) 

        formatted_json = json.dumps(indent=4)
        colorful_json = highlight(str.encode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
        print(line)
        print(colorful_json)

if __name__ == "__main__":
    run()




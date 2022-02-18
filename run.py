#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

from ast import parse
import subprocess
import argparse
import sys
import os

parser : argparse.ArgumentParser = argparse.ArgumentParser()
args : argparse.Namespace = None 
unknown_args : argparse.Namespace = None  

def parse_args():
    global args, unknown_args 
    parser.add_argument("-p", "--project", help="Project path", required=True)
    parser.add_argument("-o", "--output", help="Output path", default="./output/output.json")
    parser.add_argument("-d", "--debug", action='store_true')
    args, unknown_args = parser.parse_known_args()

def run():
    parse_args()
    # restore real path and restore arg_string
    project_mount : str = None 
    if os.path.exists(args.project):
        real_project_path = os.path.realpath(args.project)
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == args.project:
                sys.argv[i] = real_project_path
                break
        args.project = real_project_path
        project_mount = f"-v {args.project}:{args.project}"
    else:
        project_mount = '-v /tmp:/tmp'
    args.output =  os.path.realpath(args.output)
    restored_arg_string = ' '.join(sys.argv[1:])
    try: 
        process = subprocess.Popen(f"docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v go_mod:/root/go/pkg/mod -v go_cache:/root/.cache/go-build \
            {project_mount} -v {os.path.dirname(args.output)}:/unsafe-toolkit/output -it \
            unsafe-go-toolkit {restored_arg_string}", stdout=subprocess.PIPE, shell=True)
        for line in iter(process.stdout.readline, b''):  # With Python 3, you need iter(process.stdout.readline, b'') (i.e. the sentinel passed to iter needs to be a binary string, since b'' != '')
            sys.stdout.buffer.write(line)
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode("utf-8"))
        print(e.stderr.decode("utf-8"))
        raise(e)

if __name__ == "__main__":
    run()
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
    args, unknown_args = parser.parse_known_args()

def run():
    parse_args()
    # restore real path and restore arg_string
    real_project_path = os.path.realpath(args.project)
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == args.project:
            sys.argv[i] = real_project_path
            break
    args.project = real_project_path
    restored_arg_string = ' '.join(sys.argv[1:])

    try: 
        process = subprocess.Popen(f"docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v go_mod:/root/go/pkg/mod -v go_cache:/root/.cache/go-build \
            -v {args.project}:{args.project} \
            unsafe-go-toolkit {restored_arg_string}", stdout=subprocess.PIPE, shell=True)
        for line in iter(process.stdout.readline, b''):  # With Python 3, you need iter(process.stdout.readline, b'') (i.e. the sentinel passed to iter needs to be a binary string, since b'' != '')
            sys.stdout.buffer.write(line)
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode("utf-8"))
        print(e.stderr.decode("utf-8"))
        raise(e)

if __name__ == "__main__":
    run()
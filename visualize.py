#!/usr/bin/env python3 

import argparse
import json

parser : argparse.ArgumentParser = argparse.ArgumentParser()
args : argparse.Namespace = None 

def parse_args():
    global args
    parser.add_argument("-i", "--input", help="Path of input JSON file")
    parser.add_argument("-o", "--output", help="Path of output visualized file")
    args = parser.parse_args()

def visualize():
    input = json.load(open(args.input))
    # TODO: Export to markdown?
    

def run():
    parse_args()
    visualize()

if __name__ == "__main__":
    run()

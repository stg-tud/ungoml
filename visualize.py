#!/usr/bin/env python3 

import argparse
import json
import matplotlib.pyplot as plt 
import numpy as np

parser : argparse.ArgumentParser = argparse.ArgumentParser()
args : argparse.Namespace = None 

def parse_args():
    global args
    parser.add_argument("-i", "--input", help="Path of input JSON file", required = True, type = str)
    parser.add_argument("-o", "--output", help="Path of output visualized folder", type = str, default = "output/")
    args = parser.parse_args()

def visualize():
    dic = json.load(open(args.input))

    for file, lines in dic.items():
        # https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_label_demo.html
        for line, line_classifications_list in lines.items():
            # Prepare data 
            for index, line_classifications in enumerate(line_classifications_list):
                y_pos = np.arange(len(line_classifications.keys()))
                classification_probabilities = line_classifications.values()
                classification_categories = line_classifications.keys()
                # Set up graph 
                fig, ax = plt.subplots()
                ind = np.arange(len(line_classifications.keys()))
                hbars = ax.barh(y_pos, classification_probabilities, align='center')
                ax.set_yticks(y_pos, labels=classification_categories)
                ax.invert_yaxis()  # labels read top-to-bottom
                ax.set_xlabel('%s:%s' % (file, line))
                ax.set_title('Classification of unsafe usages in Go code: %d' % (index + 1) )

                plt.tight_layout()
                fig.savefig(args.output + '/%s_%s_%d.svg' % (file, line, index))
    

def run():
    parse_args()
    # Check if 
    visualize()

if __name__ == "__main__":
    run()

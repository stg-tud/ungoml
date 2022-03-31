#!/usr/bin/env python3 

import argparse
import json
import matplotlib.pyplot as plt 
import numpy as np
import os
import pathlib 

parser : argparse.ArgumentParser = argparse.ArgumentParser()
args : argparse.Namespace = None 

def parse_args():
    global args
    parser.add_argument("-i", "--input", help="Path of input JSON file", required = True, type = str)
    parser.add_argument("-o", "--output", help="Path of output visualized folder", type = str, default = "output/")
    parser.add_argument("-t", "--type", help="File type of output graphs", type = str, default = "png")
    # TODO: Threshold and formats
    args = parser.parse_args()

def visualize():
    dic = json.load(open(args.input))
    output_files = []
    
    for file, lines in dic.items():
        # https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_label_demo.html
        for line, line_classifications_list in lines.items():
            # Prepare data 
            code = line_classifications_list[0] # [1:]
            for index, line_classifications in enumerate(line_classifications_list[1:]):
                y_pos = np.arange(len(line_classifications.keys()))
                classification_probabilities = line_classifications.values()
                classification_categories = line_classifications.keys()
                # Set up graph 
                fig, ax = plt.subplots()
                ind = np.arange(len(line_classifications.keys()))
                hbars = ax.barh(y_pos, classification_probabilities, align='center')
                ax.set_yticks(y_pos, labels=classification_categories)
                ax.invert_yaxis()  # labels read top-to-bottom
                # TODO: Percentages
                ax.set_xlabel("Probability (0 - 1)")
                ax.set_title('Classification label %d of unsafe usages in %s:%s\n%s' % (index + 1, file, line, code) )

                plt.tight_layout()
                filename = '%s_%s_%d.%s' % (file, line, index, args.type)
                dirname = os.path.dirname(args.output + filename)
                if not os.path.exists(dirname):
                    pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)
                fig.savefig(args.output + filename)
                output_files.append(filename)
    
    output_html = "<html>\n"
    for file in output_files:
        output_html += "<img src=%s>\n" % (file)
    output_html += "</html>"
    with open(args.output + 'report.html', 'w') as report:
        report.write(output_html)
    print(f"Generated graphics for {len(output_files)} files.")
    

def run():
    parse_args()
    # Check if output folder exists
    if not os.path.isdir(args.output):
        os.mkdir(args.output)
    visualize()

if __name__ == "__main__":
    run()

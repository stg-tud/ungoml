## Unsafe Toolkit

The usage of the unsafe library in Go allows developers to circumvent its memory
protection and can introduce security vulnerabilities. `go-geiger` helps developers
to spot usages of unsafe in their code. Machine learning can be used to classify
the reason and context of this usage.

This toolkit should provide a wrapper / Docker container for 
https://github.com/Cortys/unsafe-go-classifier. Snippets of Go code should be given as a parameter for a container. The container will then analyze the code for unsafe usages and try to classify it. 

## Installation 

Install the `unsafe-go-classifier`.

Clone this repository with:

`git clone git@github.com:stg-tud/unsafe-toolkit.git`

## Running the analysis
 
Enter the directory:

`cd unsafe-toolkit`

Run the run.py file with the following arguments:
```
usage: run.py [-h] -f FILE [-p PROJECT] --package PACKAGE [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File name of Go file to analyze
  -p PROJECT, --project PROJECT
                        Path of package where the Go file lies in
  --package PACKAGE     Package name of Go file
  -o OUTPUT, --output OUTPUT
                        Output file of JSON file
```

## Running the visualizer 

Run the visualize.py with the following arguments:





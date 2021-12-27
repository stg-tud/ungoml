# Unsafe Toolkit

The usage of the unsafe library in Go allows developers to circumvent its memory
protection and can introduce security vulnerabilities. `go-geiger` helps developers
to spot usages of unsafe in their code. Machine learning can be used to classify
the reason and context of this usage.

This toolkit should provide a wrapper / Docker container for 
https://github.com/Cortys/unsafe-go-classifier. Snippets of Go code should be given as a parameter for a container. The container will then analyze the code for unsafe usages and try to classify it. 

## Installation 

Install [unsafe-go-classifier]("https://github.com/Cortys/unsafe-go-classifier").

Install [go-geiger]("https://github.com/stg-tud/go-geiger").

Clone this repository with:

`git clone git@github.com:stg-tud/unsafe-toolkit.git`
 
Enter the directory:

`cd unsafe-toolkit`

Install the required python packages: 

`pip install -r requirements.txt`

## Running the analysis

Run the run.py file with the following arguments to export analysis data from a file/project:
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

Run the visualize.py with the following arguments to visualize your acquired analysis:

```
usage: visualize.py [-h] [-i INPUT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of input JSON file
  -o OUTPUT, --output OUTPUT
                        Path of output visualized file
```





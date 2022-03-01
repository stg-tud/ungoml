# Unsafe Toolkit

The usage of the unsafe library in Go allows developers to circumvent its memory
protection and can introduce security vulnerabilities. `go-geiger` helps developers
to spot usages of unsafe in their code. Machine learning can be used to classify
the reason and context of this usage.

This toolkit should provide a wrapper / Docker container for
<https://github.com/Cortys/unsafe-go-classifier>. Snippets of Go code should be given as a parameter for a container. The container will then analyze the code for unsafe usages and try to classify it.

## Installation (Host)

Install [unsafe-go-classifier]("https://github.com/Cortys/unsafe-go-classifier").

Install [go-geiger]("https://github.com/stg-tud/go-geiger").

Clone this repository with:

`git clone git@github.com:stg-tud/unsafe-toolkit.git`

Enter the directory:

`cd unsafe-toolkit`

Install the required python packages:

`pip install -r requirements.txt`

## Installation (Docker machine)

Run the build command for the docker image or pull the image from the GitHub Container Registry (WIP): 
`docker build . -t unsafe-go-toolkit`

## Running the runner script for Docker

Run the run.py file with the following arguments to export analysis data from a file/project:

```
usage: run.py [-h] -p PROJECT [-o OUTPUT] [-v VISUALIZER_ARGS] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        Project path
  -o OUTPUT, --output OUTPUT
                        Output path
  -v VISUALIZER_ARGS, --visualizer-args VISUALIZER_ARGS
                        Arguments for the visualizer
  -d, --debug
```

## Running the analysis

Run the evaluate.py file with the following arguments to export analysis data from a file/project:

```
usage: evaluate.py [-h] [-p PROJECT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        Path of package where the Go file lies in
  -o OUTPUT, --output OUTPUT
                        Output file of JSON file
```

## Running the visualizer

Run the visualize.py with the following arguments to visualize your acquired analysis:

```
usage: visualize.py [-h] -i INPUT [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of input JSON file
  -o OUTPUT, --output OUTPUT
                        Path of output visualized folder
```

## Running as a docker container

You can run the analysis together with the visualizer with one docker container.

## Prerequisites

You should have the unsafe-go-classifier image downloaded and tagged as usgoc/pred:latest.

## Building the image

`sudo docker build . -t unsafe-go-toolkit`

## Running the image

To run the container, you'll need to mount the volume for the output directory. Set the `OUTPUT_DIRECTORY` variable to the output directory you want the .svg files and the report PDF file in. The arguments should be either the public cloneable git link or if left empty, the mounted `/project` folder of the container. There are additional keyworded arguments from the visualizer and analyser you can enter. (TODO)

So the command would look either like this:

`sudo docker run --rm -v ${OUTPUT_DIRECTORY}:/output unsafe-go-toolkit git@github.com:Cortys/unsafe-go-classifier.git`

Or this (with the `PROJECT_DIRECTORY` variable set):

`sudo docker run --rm -v ${PROJECT_DIRECTORY}/project -v ${OUTPUT_DIRECTORY}:/output unsafe-go-toolkit`

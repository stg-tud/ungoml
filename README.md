# Unsafe Toolkit

The usage of the unsafe library in Go allows developers to circumvent its memory
protection and can introduce security vulnerabilities. `go-geiger` helps developers
to spot usages of unsafe in their code. Machine learning can be used to classify
the reason and context of this usage.

This toolkit should provide a wrapper / Docker container for
<https://github.com/Cortys/unsafe-go-classifier>. Snippets of Go code should be given as a parameter for a container. The container will then analyze the code for unsafe usages and try to classify it.

![Overview graph of UnGoML usage](./gfx/overallArchitecture.png)

## Installation (local)

### Prerequisites

You should have the unsafe-go-classifier image downloaded and tagged as usgoc/pred:latest.
Pull the unsafe-go-classifier from <https://github.com/Cortys/unsafe-go-classifier>.

Also, install go-geiger and make sure it's located in one of your path variables.
To install the Python dependencies, run the following command `pip install -r requirements.txt`.
You may want to install these packages in a local environment instead of global: `$python3 -m venv .venv ` `$source .venv/bin/activate`.
If you want to pull SSH repositories with this tool, make sure you have working SSH access. 

## Installation (Docker machine)

### Prerequisites

You should have the unsafe-go-classifier image downloaded and tagged as usgoc/pred:latest.
Pull the unsafe-go-classifier from <https://github.com/Cortys/unsafe-go-classifier>.
Also, make sure you execute the script with a user which has access to Docker.

### Building the image

Execute the following command to build the image:

`sudo docker build . -t unsafe-go-toolkit`

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
                        Arguments for the visualizer as a string, use of input argument is not recommended
  -d, --debug           Verbose mode
```

The visualizer args should be given in quotes and will then be passed in the container. Note that the output should be in the mounted output directory, because the run.py script mounts only that directory to the host files system. 

Example usage: 

`./run.py -p https://github.com/jlauinger/go-safer.git`

## Arguments for the evaluation

Run the evaluate.py file with the following arguments to export analysis data from a file/project:

```
usage: evaluate.py [-h] [-p PROJECT] [-o OUTPUT] [-m MODE] [-d] [-c CONCURRENT_THREADS]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJECT, --project PROJECT
                        Path of package where the Go file lies in
  -o OUTPUT, --output OUTPUT
                        Output file of JSON file
  -m MODE, --mode MODE  Mode of output file, choose between the strings readable or machine
  -d, --debug           Debug mode
  -c CONCURRENT_THREADS, --concurrent-threads CONCURRENT_THREADS
                        Number of concurrent evaluation containers the script should run
```


`./evaluate.py -p git@github.com:jlauinger/go-safer.git`

## Arguments for the visualizer

Run the visualize.py with the following arguments to visualize your acquired analysis:

```
usage: visualize.py [-h] -i INPUT [-o OUTPUT] [-t TYPE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path of input JSON file
  -o OUTPUT, --output OUTPUT
                        Path of output visualized folder
  -t TYPE, --type TYPE  File type of output graphs
```

`./visualize.py -i output/output.json /output`


## Usage examples

This example runs the analysis on the go-safer repository and saves the data on a custom file location.

`./run.py -p https://github.com/jlauinger/go-safer.git -o output/go_safer.json`

This example runs the same analysis as above, but with custom visualizer args.

`./run.py -p https://github.com/jlauinger/go-safer.git -o output/go_safer.json --visualizer-args "-t svg"`

## Testing

This project can be tested using the tests.py file and the following command:

`python3 -m unittest tests.py`

You can also run the tests in Visual Studio Code, the test settings have been preconfigured.

Some tests are version and package specific, so the paths for the tests should be updated to the corresponding packages.

## Audit examples for *unsafe* usages

Our tool can guide the process of auditing *unsafe* usages by categorizing usages. 
Existing linter can identify an *unsafe* usage while their lack to provide more detailed information about their porpuse. 
One linter in this category is [gosec](https://github.com/securego/gosec) that provides an option to flag false positives with `#nosec`. 
Optinally, one can add the rule to the comment, such as `G103` for the rule that identify *unsafe* usages.
Thus, this comment helps to identify examples of *unsafe* usages that have been analyzed by a linter and manually verified. 
A simple and fast query to github results in about 370 different Go-files that make use of `#nosec G103`: <https://github.com/search?l=&q=%2F%2F%23nosec+G103+language%3AGo&type=code>.

## In-depth resources about *unsafe* usages

Several members of the Go community are engaged in sharing their knowledge and insights about the _unsafe_* API. 
Below, we list a few of these resources. 
In case, you think we missed one worthwhile reading or watching, feel free to open an issue/pull request to get it merged. 
The Table is ordered alphabetical. 

| Author | Where | Title | URL | Date | Last visit |
| ------ | ----- | ----- | --- | ---- | ------- | 
| Bowes, J. | dotGo 2019 | Shattered Mirror: An Introduction to Reflect and Unsafe | [YouTube](https://www.youtube.com/watch?v=ZJFMvWHtSAA) | Mar, 25 2019 | Jan, 13 2023 | 
| Gopher Academy Blog | Blog | Safe use of unsafe.Pointer | [Blog](https://blog.gopheracademy.com/advent-2019/safe-use-of-unsafe-pointer/) | Dec, 5 2019 | Jan, 13 2023 |
| Kochetkov, A. | Hackernoon | Golang Unsafe Type Conversions and Memory Access | [Hackernoon](https://hackernoon.com/golang-unsafe-type-conversions-and-memory-access-odz3yrl) | Mar, 15 2020 | Jan, 13 2023 |
| Lauinger, J. | dev.to | Exploitation Exercise with unsafe.Pointer in Go: Information Leak (Part 1) | [dev.to](https://dev.to/jlauinger/exploitation-exercise-with-unsafe-pointer-in-go-information-leak-part-1-1kga) | May, 13 2020 | Jan, 13 2023 | 
| Walker, J. | GopherCon 2020 | Safety Not Guaranteed: Calling Windows APIs using Unsafe & Syscall | [YouTube](https://www.youtube.com/watch?v=EsPcKkESYPA) | Dec, 22 2020 | Jan, 13 2023 | 
| Wickert, A. | BSides Berlin 2023 | Go is memory safe isn't it? | [YouTube](https://www.youtube.com/watch?v=y5xd6ryxJ3U) | Sep, 20 2020 | Jan, 13 2023 | 


## Classifier

- The implementation of classifier is available in this [Cortys/unsafe-go-classifier](https://github.com/Cortys/unsafe-go-classifier) GitHub repository and archived via [figshare](https://figshare.com/articles/software/unsafe-go-classifier/22259155). The Docker container is available via [GitHub](https://github.com/Cortys/unsafe-go-classifier/pkgs/container/usgoc%2Fpred) and archived via [figshare](https://figshare.com/articles/software/UnGoML_Prediction_Container/22266490).
- Fork of `unsafe_go_study_result` that includes our CFG generation implementation along with the data used for labelling is available in this [Cortys/unsafe_go_study_results](https://github.com/Cortys/unsafe_go_study_results) GitHub repository. 

Note, that this query is via the [GitHub Search API](https://docs.github.com/en/rest/search?apiVersion=2022-11-28#timeouts-and-incomplete-results) and result in incomplete and may differentiating results. 

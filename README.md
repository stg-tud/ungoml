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

Enter the directory:

`cd unsafe-toolkit`

Build the docker image using the Dockerfile in the folder.

`docker build . -t stg-tud/unsafe-toolkit`

## Running 
 
Run the container and replace the keyword `snippet` with the path of the snippet file you want analyzed.

`docker run --rm stg-tud/unsafe-toolkit -v snippet:/code.go -v /var/run/docker.sock:/var/run/docker.sock` 

### Environment variables:

TBD



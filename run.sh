#!/usr/bin/env bash

# copy to dummy project

[ -z $1 ] && echo "No filename given!" && exit 1 

# build dummy go file 
echo "package main" > dummy_project/main.go
cat $1 >> dummy_project/main.go 

# set variables
CLASSIFIER_PATH=../
# unsafe-go-classifier
#export PROJECTS_DIR=$(realpath $(dirname $1))
#echo $PROJECTS_DIR
export PROJECTS_DIR=$(realpath .)
export FILENAME="main.go"
#FILENAME=$(basename $1)
#echo $FILENAME

# go geiger, extract lines only
LINES=$(go-geiger --show-code ./dummy_project | grep .go: | cut -d ':' -f 2)
while IFS= read -r line ;
 do echo Line: $line; 
 # unsafe-go-classifier
 # echo ${CLASSIFIER_PATH}/unsafe-go-classifier/predict.sh --project dummy_project --line $line --package main --file $FILENAME predict -m WL2GNN 
 ${CLASSIFIER_PATH}/unsafe-go-classifier/predict.sh --project dummy_project --line $line --package dummy_project --file $FILENAME predict -m WL2GNN 
 # use package in go.mod
done <<< "$LINES"

# custom args
# echo $LINE
# ${CLASSIFIER_PATH}/unsafe-go-classifier/predict.sh --project . --line 19 --package dummy_project --file $FILENAME predict -m WL2GNN


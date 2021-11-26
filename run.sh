#!/usr/bin/env bash

# copy to dummy project

[ -z $1 ] && echo "No filename given!" && exit 1 

echo "package main" > dummy_project/main.go
cat $1 >> dummy_project/main.go 

# go-geiger



CLASSIFIER_PATH=../
# unsafe-go-classifier
#export PROJECTS_DIR=$(realpath $(dirname $1))
#echo $PROJECTS_DIR
export PROJECTS_DIR=$(realpath dummy_project)
export FILENAME="main.go"
#FILENAME=$(basename $1)
#echo $FILENAME

LINES=$(go-geiger --show-code ./dummy_project | grep .go: | cut -d ':' -f 2)
while IFS= read -r line ;
 do echo $line; 
 ${CLASSIFIER_PATH}/unsafe-go-classifier/predict.sh --project . --line 19 --package main --file $FILENAME predict -m WL2GNN
done <<< "$LINES"

# custom args
# echo $LINE
# ${CLASSIFIER_PATH}/unsafe-go-classifier/predict.sh --project . --line 19 --package dummy_project --file $FILENAME predict -m WL2GNN


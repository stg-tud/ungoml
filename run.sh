#!/usr/bin/env bash

CLASSIFIER_PATH=../

export PROJECTS_DIR=$(realpath $(dirname $1))
echo $PROJECTS_DIR
FILENAME=$(basename $1)
echo $FILENAME

# custom args
# ${CLASSIFIER_PATH}/unsafe-go-classifier/predict.sh --package main --line 2 --snippet "unsafe.Pointer(oldConfig)," --file $FILENAME predict -m WL2GNN
# ${CLASSIFIER_PATH}/unsafe-go-classifier/src/usgoc/run_prediction.py --package main --file $FILENAME predict --model -m WL2GNN
${CLASSIFIER_PATH}/unsafe-go-classifier/predict.sh --project . --line 19 --package dummy_project --file $FILENAME predict -m WL2GNN


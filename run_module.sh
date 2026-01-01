#!/bin/bash
# Helper script to run modules with correct PYTHONPATH

export PYTHONPATH=$(pwd)
python "$@"

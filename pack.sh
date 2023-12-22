#!/bin/bash

NAME="xzbori20"

zip -r $NAME.zip ./*.md ./*.py requirements.txt ./tests/

zip -r $NAME"_testing_data.zip" ./data_testing_5min/

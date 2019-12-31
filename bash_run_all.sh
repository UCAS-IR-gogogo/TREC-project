#!/usr/bin/env bash
cd ./deep_model/
python train.py
cd ..
python main.py  --run_all --create_index --print_topics --use_retrain_parameter
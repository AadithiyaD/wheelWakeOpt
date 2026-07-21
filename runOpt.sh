#!/bin/sh

rm -rf cases/*
rm -rf ax_result_data/*

python3 centralControl.py
python3 bayesOpt.py
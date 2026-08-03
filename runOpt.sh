#!/bin/sh

rm -rf cases/*
rm -rf ax_result_data/*
rm -rf 0/

cp -r 0.orig/ 0/
python3 centralControl.py
python3 bayesOpt.py
#!/bin/bash
python3 master.py &
python3 slave-template.py &
python3 plot.py

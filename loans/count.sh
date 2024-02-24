#!/bin/bash

wget https://pages.cs.wisc.edu/~harter/cs544/data/hdma-wi-2021.zip

unzip hdma-wi-2021.zip

count=$(grep -r "Multifamily" hdma-wi-2021.csv | wc -l)
echo $count


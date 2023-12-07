#!/bin/bash

if [ -d output ]; then
  mv output output.bak
fi

mkdir -p output

cd output

for d in `seq -f "dataset-%04g" 1 20`; do
  echo $d
  mkdir $d
  echo $d >> list.dat
done

#!/bin/sh

njob=${1:-64}
echo "number of dataset: $njob"

for d in `seq -f 'dataset_%04g' 1 $njob`
do
	if [ ! -d $d ]; then
		mkdir -p $d
	fi
done

ls -1d dataset_* > list.dat

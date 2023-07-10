#!/bin/bash

for f in $@
do
    # awk -F'\t' -i inplace -v INPLACE_SUFFIX=_bak '{ if (NR == 1 || $7 == 0) print }' $f
    awk -F'\t' -i inplace -v INPLACE_SUFFIX=_bak '{ if (NR == 1 || $7 != 255) print }' $f
done

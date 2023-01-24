#!/bin/bash

containers=("default" "to_run")

for i in ${!containers[@]};
do
    c=${containers[i]}
    echo "[Container] '$c'"
    docker build -t assbot:$c -f $c .
done

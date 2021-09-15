#!/bin/bash
app="cse.tools"
docker build -t ${app} .
docker run -d -it -p 56733:80 \
  --name=${app} \
  -v $PWD:/app ${app}
#!/usr/bin/env bash

pwd
mkdir modules/mc-client -p
cd modules/mc-client
pwd
ls -la

curl -L https://github.com/gis4dis/mc-client/releases/download/v1.8/release.tar.gz | tar xvz

#!/bin/bash

pyenv local 2.7
export APPLICATION_ID=dev~gae1st
dev_appserver.py --enable_console --support_datastore_emulator=true --application=gae1st --enable_host_checking=false --host 0.0.0.0 --port 8027 .

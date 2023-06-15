#!/bin/bash

pyenv local 3.7.16
export APPLICATION_ID=dev~gae2nd
export CLOUDSDK_DEVAPPSERVER_PYTHON=/Users/nguyen.van.vuong/.pyenv/versions/2.7.18/bin/python2.7
dev_appserver.py --support_datastore_emulator=true --application=gae2nd --threadsafe_override=false --max_module_instances=1 --enable_host_checking=false --host 0.0.0.0 --port 8037 .



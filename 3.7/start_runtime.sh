#!/bin/bash

pyenv local 2.7.18
export APPLICATION_ID=dev~gae2nd
export CLOUD_SDK_ROOT=/Users/nguyen.van.vuong/Data/Install/google-cloud-sdk/bin
export CLOUDSDK_DEVAPPSERVER_PYTHON=/Users/nguyen.van.vuong/.pyenv/versions/2.7.18/bin/python2.7
export PYTHON27=/Users/nguyen.van.vuong/.pyenv/versions/2.7.18/bin/python2.7
export PYTHON3=/Users/nguyen.van.vuong/.pyenv/versions/3.7.16/bin/python3.7
python $CLOUD_SDK_ROOT/dev_appserver.py --runtime_python_path="python27=$PYTHON27,python3=$PYTHON3" --support_datastore_emulator=true --application=gae2nd --threadsafe_override=false --max_module_instances=1 --enable_host_checking=false --host 0.0.0.0 --port 8037 .



#!/usr/bin/env bash

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Author: Steffen70 <steffen@seventy.mx>
# Creation Date: 2024-07-25
#
# Contributors:
# - Contributor Name <contributor@example.com>

generatedDirectory="generated"

# Clear generated directory
rm -rf "./$generatedDirectory"

mkdir -p "./$generatedDirectory"

currentDirectory=${PWD##*/}

# Array of proto files
protosArray=("model" "strategy" "playing_field")

# Base protoc command
protoCommand="python -m grpc_tools.protoc --proto_path=$PROTOBUF_PATH --python_out=./${generatedDirectory} --grpc_python_out=./${generatedDirectory}"

# Add proto files to the command
for proto in "${protosArray[@]}"; do
    protoCommand+=" $PROTOBUF_PATH/${proto}.proto"
done

# Execute the final protoc command
eval $protoCommand

#!/bin/bash -e
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#


set -eux

cd `dirname $0`/..
export TMPDIR=`mktemp -d`
trap "rm -rf $TMPDIR" EXIT
SWAGGER_CODEGEN_DIRECTORY=${SWAGGER_CODEGEN_DIRECTORY:-'..'}

generate() {
  JSON_FILE=${1}
  MODEL_DIR=${2:""}
  
  java -jar ${SWAGGER_CODEGEN_DIRECTORY}/modules/swagger-codegen-cli/target/swagger-codegen-cli.jar \
    generate -i k8sclient/templates/${JSON_FILE} -l python -o $TMPDIR
    
  cp $TMPDIR/swagger_client/apis/api* $PWD/k8sclient/client/apis
  
  rm $PWD/k8sclient/client/models/${MODEL_DIR}/*.py || true
  cp $TMPDIR/swagger_client/models/* ./k8sclient/client/models/${MODEL_DIR}
}

generate batch_v1.json batch
generate extensions_v1beta1.json extensions_beta

generate v1.json
cp $TMPDIR/swagger_client/*.py ./k8sclient/client/

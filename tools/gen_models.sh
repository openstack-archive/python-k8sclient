#!/bin/bash -e

cd `dirname $0`/..

generate() {
  JSON_FILE=${1}
  MODEL_DIR=${2}
  
  rm -rf ./tmp
  java -jar ../swagger-codegen/modules/swagger-codegen-cli/target/swagger-codegen-cli.jar \
    generate -i k8sclient/templates/${JSON_FILE} -l python -o ./tmp
    
  cp ./tmp/swagger_client/apis/api* ./k8sclient/client/apis
  
  rm ./k8sclient/client/models/${MODEL_DIR}/*.py
  cp ./tmp/swagger_client/models/* ./k8sclient/client/models/${MODEL_DIR}
}

generate batch_v1.json batch
generate extensions_v1beta1.json extensions_beta

generate v1.json
cp ./tmp/swagger_client/*.py ./k8sclient/client/

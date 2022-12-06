FUNCTION_NAME="slack-coffee-matcher-bot"
BUILD_PATH=${PWD}/package.zip

aws lambda update-function-code \
    --function-name ${FUNCTION_NAME} \
    --zip-file fileb://${BUILD_PATH}
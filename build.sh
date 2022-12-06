rm -rf package
rm package.zip

mkdir package

pip install -r requirements.txt -t package
cp *.py config.yaml package

(cd package && zip -r ../package.zip *) > /dev/null

rm -rf package
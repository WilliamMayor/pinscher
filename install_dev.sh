#! /bin/sh

virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

curl https://apsw.googlecode.com/files/apsw-3.7.15.2-r1.zip > apsw.zip
unzip apsw.zip
cd apsw-3.7.15.2-r1
python setup.py fetch --all build --enable-all-extensions install
cd ..
rm -rf apsw.zip apsw-3.7.15.2-r1
#!/bin/sh
virtualenv -p /usr/bin/python3.2 venv
source venv/bin/activate
pip install django==1.6
pip install pysqlite

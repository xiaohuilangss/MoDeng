# encoding=utf-8

from jqdatasdk import *
import json

from Config.AutoGenerateConfigFile import data_source_url

with open(data_source_url, 'r') as f:
    r = json.load(f)

auth(r['JQ_Id'], r['JQ_passwd'])
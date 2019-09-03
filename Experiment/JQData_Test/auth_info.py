# encoding=utf-8
import jqdatasdk
from jqdatasdk import *
import json

with open('c:/JQ_ID_info.json', 'r') as f:
    r = json.load(f)

auth(r['ID'], r['SC'])
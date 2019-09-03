# encoding=utf-8
# from JQData_Test.auth_info import *
from JQData_Test.JQ_Industry_Analysis_Sub import *
from SDK.MyTimeOPT import get_current_date_str

df = jqdatasdk.get_price(normalize_code('002773'), count=1, end_date=get_current_date_str())

df = jqdatasdk.get_price(normalize_code('002773'), frequency='daily', count=300, end_date=get_current_date_str())

end = 0

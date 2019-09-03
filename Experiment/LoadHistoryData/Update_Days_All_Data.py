# encoding = utf_8
from SDK.SDKHeader import *

for datetime in pd.date_range('2001-01-01',get_current_date_str()):
    date = str(datetime)[0:10]
    if not is_table_exist(conn=conn_days_all,database_name=stk_days_all_data_db_name,table_name='day'+date):
        day_data = ts.get_day_all(str(date))
        if isinstance(day_data,pd.DataFrame) :
            day_data.to_sql(con=engine_days_all, name='day'+date, if_exists='append', schema=stk_days_all_data_db_name, index=False)
        else:
            print('没有日期为' + date + '的全天数据！')
    else:
        print('日期为' + date + '的全天数据在数据库中已经存在！')
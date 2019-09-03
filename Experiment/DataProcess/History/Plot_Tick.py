#encoding=utf-8

from Config.GlobalSetting import *
from Restore.AnalysisSub import get_average_array_span,plot_x_date

stk_code = '300508'
field_param = 'net_total_in'

tick_df = get_total_table_data(conn=conn_tick,table_name='tick'+stk_code)

# 将数据中的NaN替换为0
tick_df = tick_df.fillna(0)


tick_df['net_big_in'] = tick_df['big_in'] - tick_df['big_out']
tick_df['net_total_in'] = tick_df['total_in'] - tick_df['total_out']

ave_df = get_average_array_span(df_param=tick_df,array_span_param=[7,20,60],field_param=field_param)


y_attri = [
# ("net_big_in","go--",U"净大单流入"),
(field_param+"mean7","k*--",U"7日均值"),
(field_param+"mean20","ro--",U"20日均值"),
(field_param+"mean60","b*--",U"60日均值"),
# ("mean10","yo--",U"10日均值"),
("net_total_in","m*--",U"净总流入")
]

plot_x_date(code_param=stk_code,data_df_param=ave_df,y_axis_info_param=y_attri)

end = 0


# encoding = utf-8
from sdk.SDKHeader import *

def gen_trend_graph():
    file_url = "F:/MYAI/文档资料/用于读取的文件/av_trend_record/"+'av_trend' + get_current_date_str()+'.csv'

    # 图片保存路径
    save_dir = "F:/MYAI/文档资料/用于读取的文件/av_trend_record/"+get_current_date_str()+'均值趋势分析/'


    with open(file_url) as f:
        trend_df = pd.read_csv(f)


    # 获取180均线趋势前30
    plot_high_level(trend_df,180,save_dir)


    # 获取60均线趋势前30
    plot_high_level(trend_df,30,save_dir)


    # 获取30均线趋势前30
    plot_high_level(trend_df,14,save_dir)



# ----------------------------------测试------------------------------------------

# gen_trend_graph()



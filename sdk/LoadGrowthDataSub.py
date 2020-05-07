# encoding = utf-8

from sdk.SDKHeader import *

mpl.rcParams['font.sans-serif'] = ['SimHei']


# 从growth数据库中获取每个stk的数据，转成Dataframe后按时间升序排序，返回！
def getSingleStkGrowth(codeParam):

    result = []
    for year in range(2001,int(get_current_date_str().split('-')[0]) +1):
        for quarter in range(1,5):
            table_name = 'growth' + str(year)+'0'+str(quarter)
            if (int(str(year)+'0'+str(quarter)) < int(get_quarter_date())) & is_table_exist(conn_growth,stk_growth_data_db_name,table_name):
                growth_df = get_total_table_data(conn=conn_growth,table_name = table_name)
                singleGrowth = growth_df[growth_df.code == codeParam]\
                .reset_index(drop=True)\
                .to_dict(orient='index')

                if len(singleGrowth):
                    singleGrowth = singleGrowth[0]
                    singleGrowth.update({'date':str(year)+'0'+str(quarter)})
                    result.append(singleGrowth)

    return DataFrame(result).sort_values(by='date',ascending=True)


def plot_stk_growth(codeParam):

    singleGrowth = getSingleStkGrowth(codeParam)

    # trick to get the axes
    fig, ax = plt.subplots()

    # plot data
    ax[0].plot(singleGrowth['date'], singleGrowth['mbrg'], 'go--', label=U'主营业务收入增长率')
    ax[0].plot(singleGrowth['date'], singleGrowth['nprg'], 'b*--', label=U'净利润增长率')
    ax[0].plot(singleGrowth['date'], singleGrowth['nav'], 'cv--', label=U'净资产增长率')
    ax[0].plot(singleGrowth['date'], singleGrowth['targ'], 'g*--', label=U'总资产增长率')
    ax[0].plot(singleGrowth['date'], singleGrowth['epsg'], 'k*--', label=U'每股收益增长率')
    ax[0].plot(singleGrowth['date'], singleGrowth['seg'], 'r*--', label=U'股东权益增长率')


    xticklabels = list(singleGrowth['date'])
    ax[0].set_xticklabels(xticklabels, rotation=90)
    ax[0].set_title('growth' + codeParam)
    ax[0].legend(loc='best')
    plt.show()


# encoding = utf-8

from Config.GlobalSetting import *
from sdk.AboutTimeSub import stdMonthDate

ppi_df = ts.get_ppi()

# trick to get the axes
fig, ax = plt.subplots()
std_date = list(map(lambda x: stdMonthDate(x),ppi_df['month']))

# plot data
ax.plot(std_date, ppi_df['ppiip'], 'go--', label=U'工业品出厂')
ax.plot(std_date, ppi_df['ppi'], 'b*--', label=U'生产资料')
ax.plot(std_date, ppi_df['qm'], 'cv--', label=U'采掘工业')
ax.plot(std_date, ppi_df['rmi'], 'g*--', label=U'原材料工业')
ax.plot(std_date, ppi_df['pi'], 'k*--', label=U'加工工业')
ax.plot(std_date, ppi_df['cg'], 'm*--', label=U'生活资料')

ax.plot(std_date, ppi_df['food'], 'r*--', label=U'食品类')
ax.plot(std_date, ppi_df['clothing'], 'y^-', label=U'衣着类')
ax.plot(std_date, ppi_df['roeu'], 'y*--', label=U'一般日用品')
ax.plot(std_date, ppi_df['dcg'], 'y*:', label=U'耐用消费品')

xticklabels = list(std_date)
xticklabels.reverse()
ax.set_xticklabels(xticklabels, rotation=90)
ax.set_title('各种价格指数')
ax.legend(loc='best')
plt.show()
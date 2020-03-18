# encoding=utf-8

"""
class about statistical learning
"""

from DataSource.auth_info import jq_login
from DataSource.stk_data_class import StkData


class AverageStatics(StkData):
    def __init__(self, stk_code):
        super().__init__(stk_code)
        self.down_day_data()
        
    def add_average_line(self, m):
        self.data['m_'+str(m)] = self.data['close'].rolling(window=m).mean()

    def add_average_pn(self, m):
        """
        m：mean
        pn：positive，negative
        :param m:
        :return:
        """
        self.data['m_pn_'+str(m)] = self.data.apply(lambda x: x['close']-x['m_'+str(m)] >= 0, axis=1)

    def add_pn_pot(self, m):
        """
        找出穿越m线的点
        :return:
        """
        self.data['m_pn_last_'+str(m)] = self.data['m_pn_'+str(m)].shift(1)
        self.data['pn_pot_'+str(m)] = self.data.apply(lambda x: x['m_pn_'+str(m)] != x['m_pn_last_'+str(m)], axis=1)
    

if __name__ == '__main__':
    
    jq_login()
    self = AverageStatics('000001')
    self.down_day_data(count=1000)
    self.add_average_line(20)
    m=20
    self.data
    end = 0
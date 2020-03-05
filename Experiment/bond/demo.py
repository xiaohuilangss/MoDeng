# encoding=utf-8

"""

本脚本对可转债数据进行研究
"""
from DataSource.auth_info import jq_login
from jqdatasdk import bond, query

if __name__ == '__main__':
    jq_login()

    df = bond.run_query(query(bond.BOND_BASIC_INFO).filter(bond.BOND_BASIC_INFO.bond_form_id == '703013'))

    end = 0
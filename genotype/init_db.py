'''
初始化数据库：
1、存入标记信息
2、样品信息
'''

import os
import sys
import json
import argparse
import uuid
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../common")))
from sql_cur import SqlCur


def sample_filter(df):
    """样品信息过滤

    Args:
        df (_type_): DataFrame
    """
    new_df = df.iloc[:, 1:4].copy()
    new_df.columns = [0,1,2]
    new_df.dropna(axis=0, inplace=True)

    filter_df = new_df[
        (~new_df[0].str.contains("NTC"))
        &(~new_df[0].str.contains("SK"))
        &(~new_df[0].str.contains("GMO"))
        &(~new_df[1].str.contains("XLW", na=False))
    ]

    filter_df[0].replace("杂交种对照", "CK")
    filter_df[0].replace("ck", "CK")

    return filter_df



def init_db(config:dict):
    '''
    初始化数据库
    '''
    cur = SqlCur(config["db_path"])
    try:
        # 初始化数据库表结构
        cur.init_table()
        # 初始化标记信息表
        probeset_df = pd.read_csv(config["probeset_file_path"])
        probeset_df.to_sql(
            "Probeset",
            getattr(cur, "conn"),
            if_exists="replace",
            index=False,
        )

        # 初始化样品信息表
        sample_table = pd.ExcelFile(config["sample_file_path"])
        sample_table_sheets = sample_table.sheet_names
        for sheet_name in sample_table_sheets:
            print(sheet_name)
            sheet_df = sample_table.parse(sheet_name)
            filter_df = sample_filter(sheet_df)
            filter_df[3] = sheet_name
            filter_df[4] = filter_df.apply(lambda _: str(uuid.uuid4()), axis=1)

            filter_df.columns = ["sample_barcode", "sample_name", "call_code", "board_code", "id"]

            filter_df.to_sql(
                "Sample",
                getattr(cur, "conn"),
                if_exists="append",
                index=False
            )

    except Exception as e:
        print(e)
    finally:
        # 关闭数据库连接
        cur.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python ',
        description=''
    )
    parser.add_argument("-c", "--config", help="input config file path", type=argparse.FileType("r"), required=True)
    args = parser.parse_args()

    with open(args.config.name, "r", encoding="utf-8_sig") as f:
        config = json.load(f)

    init_db(config)

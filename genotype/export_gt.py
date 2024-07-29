'''
根据查询条件导出样本的基因型数据
'''

import os
import sys
import json
import argparse
from datetime import datetime

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../common")))
from sql_cur import SqlCur


def export_gt(config:dict):
    '''
    导出基因型数据
    '''
    cur = SqlCur(config["db_path"])
    try:
        probeset_df = pd.read_sql("SELECT * FROM Probeset;", getattr(cur, "conn"))

        data = pd.DataFrame()
        for item in config["query"]:
            querys = []

            for key, value in item.items():
                querys.append(f"{key} like '%{value}%'")

            sql_str = f"SELECT * FROM Sample WHERE {' AND '.join(querys)} AND genotype IS NOT NULL;"

            item_df = pd.read_sql(
                sql_str,
                getattr(cur, 'conn')
            )

            data = pd.concat([data, item_df])

        for _, row in data.iterrows():
            probeset_df[row["id"]] = eval(row["genotype"])
        
        current_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        with pd.ExcelWriter(f"{config['output']}/{current_time}.xlsx") as writer:
            probeset_df.to_excel(writer, sheet_name="Genotype", index=False)
            data[["id","sample_barcode", "sample_name", "board_code"]].to_excel(writer, sheet_name="Sample Info", index=False)

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

    export_gt(config)
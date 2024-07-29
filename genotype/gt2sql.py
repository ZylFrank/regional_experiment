'''
将原始的基因型数据存入数据库
'''
import os
import sys
import json
import argparse

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../common")))
from sql_cur import SqlCur


def gt2sql(config:dict):
    """基因型数据写入数据库
    Args:
        config (dict): _description_
    """
    cur = SqlCur(config["db_path"])
    try:
        # 获取标记信息表
        probeset_df = pd.read_sql("SELECT * FROM Probeset;", getattr(cur, "conn"))
        
        # 获取板上样本
        for board_code, file_path in config["gt_files_path"].items():
            print(f"Current board code is: {board_code}")
            gt_df = pd.read_excel(file_path)
            board_samples = cur.get_items("Sample", "board_code", board_code)

            board_data = []

            for _, row in board_samples.iterrows():
                if row["call_code"] in gt_df.columns:
                    sample_gt_df = gt_df[["probeset_id", row["call_code"]]]
                    format_gt_df = pd.merge(probeset_df, sample_gt_df, on="probeset_id", how="left")
                    sample_gts = format_gt_df[row["call_code"]].tolist()

                    board_data.append({
                        "id": row["id"],
                        "genotype": str(sample_gts),
                    })

            # update many
            cur.update_many(
                "Sample",
                "id",
                board_data
            )


    except Exception as e:
        print(e)
    finally:
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

    gt2sql(config)

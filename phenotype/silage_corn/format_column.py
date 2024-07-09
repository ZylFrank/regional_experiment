'''
统一格式化表头
'''
import os
import argparse
import json
import pandas as pd
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../../common")))
from base import get_folder_files, save_file

MAPS={}


def col_finder(col):
    new_col = ""
    for key, value in MAPS.items():
        if col in value:
            new_col = key
            break
    return new_col


def check_column(cols:list):
    global MAPS
    new_cols = []
    for col in cols:
        if col not in MAPS: # 非标准表头
            new_col = col_finder(col)
            if new_col == "":
                input_data = input(f"是否对'{col}'进行表头映射?(y/n)")
                while input_data not in ["Y", "y", "N", "n"]:
                    input_data = input("是否进行表头映射?(y/n)")

                if input_data in ["Y", "y"]:
                    new_name = input("请输入标准名称:")
                    if new_name in MAPS:
                        MAPS[new_name].append(col)
                        new_cols.append(new_name)
                    else:
                        data_type = input("请输入数据类型:(int/float/str)")
                        MAPS[new_name]=[data_type, col]
                        new_cols.append(new_name)
                else:
                    pass
            else:
                new_cols.append(new_col)
        else:
            new_cols.append(col)
    return new_cols



def format_column(fp:str, output)->None:
    files_path = get_folder_files(fp)
    for file_path in files_path:
        # 只处理分析分级结果
        if file_path[-6:-4:] == "结果":
            print(file_path)
            df = pd.read_csv(file_path)
            df_columns = df.columns.to_list()
            new_columns = check_column(df_columns)
            df.columns = new_columns
            new_file_path = file_path.replace(fp, output)
            print(f"file saved: {new_file_path}")
            save_file(df, new_file_path)
            print(MAPS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python format_column',
        description='format columns of table'
    )
    parser.add_argument("-c", "--config", help="input config file path", type=argparse.FileType("r"), required=True)
    args = parser.parse_args()

    with open(args.config.name, "r") as f:
        config = json.load(f)

    MAPS = config['maps']

    format_column(config['folder_path'],  config['output'])

    # update config file
    print("update config file")
    with open(args.config.name, "w", encoding="utf-8") as f:
        json.dump({
            "folder_path": config['folder_path'],
            "output": config['output'],
            "maps": MAPS
        }, f)

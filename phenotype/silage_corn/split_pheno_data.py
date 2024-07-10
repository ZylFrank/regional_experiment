'''
根据表型字段单独提取表型数据
'''
import os
import argparse
import json
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../../common")))
from base import get_folder_files, save_file



def split_pheno_data(config):
    files_path = get_folder_files(config["folder_path"])

    final_dfs = {}
    for k in config["keys"]:
        final_dfs[k] = pd.DataFrame()

    for file_path in files_path:
        df = pd.read_csv(file_path)
        for k in config["keys"]:
            if k in df.columns:
                k_df = df[config["must_include"] + [k]]
                final_dfs[k] = pd.concat([final_dfs[k], k_df])

    for key, k_df in final_dfs.items():
        new_file_path = f'{config["output"]}/{key}.csv'
        save_file(k_df, new_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python split_pheno_data',
        description='split phenotype data one by one'
    )
    parser.add_argument("-c", "--config", help="input config file path", type=argparse.FileType("r"), required=True)
    args = parser.parse_args()

    with open(args.config.name, "r", encoding="utf-8_sig") as f:
        config = json.load(f)

    split_pheno_data(config)


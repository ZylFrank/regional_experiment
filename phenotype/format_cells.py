'''
批量格式化单元格数据
'''
import os
import traceback
import pandas as pd
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../common")))
from base import get_folder_files, save_file

# 要处理的文件目录
INPUT="/Users/zyl/Documents/区试数据/表型/2013_表型整理-王伟伟/02. 2013_东北早熟春玉米组"
# 文件处理后的输出路径
OUTPUT="/Users/zyl/Documents/区试数据/表型/格式化后/test"

# 定义需要清除的特殊字符
NEED_CLEAR_STR=[" ", "\n", "\r", "\r\n"]
# 定义需要替换的字符
STR_REPLACE = {
    "（":"(",
    "）":")",
    "Cm":"cm",
    "CM":"cm",
    "cM":"cm",
}

def format_str(s):
    """
    格式化单元格字符
    """
    new_s = s
    if type(s) == str:
        for o_s in NEED_CLEAR_STR:
            if o_s in new_s:
                new_s = new_s.replace(o_s, "")

        # 字符串替换
        for key, value in STR_REPLACE.items():
            if key in new_s:
                new_s = new_s.replace(key, value)

        return new_s
    else:
        return new_s



def format_cel_by_file(fp):
    """表格数据格式化

    Args:
        fp (str): file path
    """
    if fp.split(".")[-1] in ["xlsx"]:
        table_df = pd.read_excel(fp, header=None)
    else:
        table_df = pd.read_csv(fp, header=None)
    col_names = table_df.columns.tolist()
    for index, row in table_df.iterrows():
        for col in col_names:
            cel_txt = row[col]
            table_df.at[index, col] = format_str(cel_txt)

    return table_df


if __name__ == "__main__":
    try:
        files_path = get_folder_files(INPUT)
        for fp in files_path:
            print(">", fp)
            new_file_path = fp.replace(INPUT, OUTPUT)
            df = format_cel_by_file(fp)
            save_file(df, new_file_path, header=False)

    except Exception as e:
        traceback.print_exc()

'''
公用方法
'''
import os
import hashlib
import pandas as pd


def get_folder_files(fp):
    '''
    递归检查每个目录的文件
    '''
    files_path = []
    dir_list = [name for name in os.listdir(fp) if name[0] not in ["~", "."]]
    for dir_name in dir_list:
        if os.path.isdir(f"{fp}/{dir_name}"):
            files_path += get_folder_files(f"{fp}/{dir_name}")
        else:
            files_path.append(f"{fp}/{dir_name}")
    return files_path


def save_file(df, fp, **args):
    """
    保存数据表
    """
    new_file_path = f'{".".join(fp.split(".")[:-1])}.csv'
    last_index = new_file_path.rindex("/")
    folder_path = new_file_path[:last_index]

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    df.to_csv(new_file_path, index=False, encoding="utf-8_sig", **args)


def md5_id(contexts:list)->str:
    """生成表型记录的ID

    Args:
        contexts (_list_): _description_
    Returns:
        _str_: md5
    """
    md5 = hashlib.md5()
    md5.update("-".join([str(v) for v in contexts]).encode("utf-8"))
    return md5.hexdigest()

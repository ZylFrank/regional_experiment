"""
sqlite curson
"""

import os
import sqlite3
import json
import time
import pandas as pd

TABLE_COLUMNS_MAP = {
    "Probeset": {
        "probeset_id": ["TEXT PRIMARY KEY NOT NULL", "探针ID"],
        "chr_id": ["TEXT", "染色体"],
        "start": ["INTEGER", "物理位置"],
        "markertype": ["TEXT", "标记类型"],
    },
    "Sample": {
        "id": ["TEXT PRIMARY KEY NOT NULL", "ID"],
        "sample_barcode": ["TEXT", "样品条码号"],
        "sample_name": ["TEXT", "样品名称"],
        "call_code": ["TEXT", "样品试验编号"],
        "board_code": ["TEXT", "实验板号"],
        "genotype": ["TEXT", "基因分型"],
    },
}


class SqlCur:
    """
    封装相关数据库操作方法
    """

    def __init__(self, db_url):
        self.conn = sqlite3.connect(db_url, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.table_columns_map = TABLE_COLUMNS_MAP

    def init_table(self):
        for table_name, cols in self.table_columns_map.items():
            cols_sql = []
            for key, value in cols.items():
                cols_sql.append(f"{key} {value[0]}")

            table_sql = ",".join(cols_sql)
            self.create_new_table(table_name, table_sql)

    def dict_factory(self, row):
        """_summary_

        Args:
            cursor (_type_): _description_
            row (_type_): _description_

        Returns:
            _type_: _description_
        """
        d = {}
        for idx, col in enumerate(self.cur.description):
            d[col[0]] = row[idx]
        return d


    def create_new_table(self, table_name: str, sql_str: str)->None:
        """create a new table, table will be deleted if it already exists!
        Args:
            table_name (str): 表名
            sql_str (str): 列名及数据类型
        """
        self.cur.execute(f"DROP TABLE IF EXISTS {table_name};")
        self.cur.execute(f"CREATE TABLE {table_name} ({sql_str});")
        self.conn.commit()

    def update_columns(self, table_name: str)->None:
        """给表新增字段

        Args:
            table_name (str): 表名
            values (dict): 新增的列名键值对
        """
        row = self.cur.execute(f"SELECT * FROM {table_name}").fetchone()
        row_dict = self.dict_factory(row)
        columns = list(row_dict.keys())

        # 参数检查
        validate_values = {}
        for key, value in self.table_columns_map[table_name].items():
            if key not in columns:
                validate_values[key] = value
                self.cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {key} {value[0]};")

        self.conn.commit()

    def save_records(self, table_name: str, primary_key: str, values: list):
        """批量存储记录，如果存在就更新，如果不存在就新增

        Args:
            table_name (str): _description_
            primary_key (str): _description_
            values (_type_): _description_
        """
        columns = list(values[0].keys())
        primary_keys = [item[primary_key] for item in values if primary_key in item]
        if len(primary_keys) != len(values):
            raise Exception(
                "The number of primary keys is inconsistent with the number of records"
            )
        else:
            df = pd.read_sql(
                f"SELECT {primary_key} FROM {table_name} WHERE {primary_key} IN {tuple(primary_keys)}",
                self.conn,
            )
            update_records = [item for item in values if item[primary_key] in df[primary_key].tolist()]
            insert_records = [list(item.values()) for item in values if item[primary_key] not in df[primary_key].tolist()]
            # update records
            self.update_many(
                table_name,
                primary_key,
                update_records
            )
            # insert records
            self.insert_many(
                table_name,
                columns,
                insert_records,
            )

    def update_many(self, table_name:str, primary_key: str, values:list)->None:
        """根据记录主键，更新记录的字段值

        Args:
            table_name (str): _description_
            primary_key (str): _description_
            columns (list): _description_
            values (list): _description_
        """
        for item in values:
            record_keys = []
            record_values = []
            for key, value in item.items():
                if key != primary_key:
                    record_keys.append(key)
                    record_values.append(value)

            set_sql = ",".join([f"{key}=?" for key in record_keys])

            self.cur.execute(
                f"UPDATE {table_name} SET {set_sql} WHERE {primary_key} = ?",
                tuple(record_values+[item[primary_key]])
            )

        self.conn.commit()


    def insert_many(self, table_name: str, columns: list, values: list):
        """插入的是数据库中主键不存在的值，如果存在会报错

        Args:
            table_name (_type_): _description_
            columns (_type_): _description_
            values (_type_): _description_
        """
        self.cur.executemany(
            f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({','.join(['?']*(len(columns)))});",
            values,
        )
        self.conn.commit()

    def get_item(self, table_name: str, column_name: str, value: str) -> dict:
        """通过列名查询单条记录

        Args:
            table_name (str): _description_
            column_name (str): _description_
            value (str): _description_

        Returns:
            dict: _description_
        """
        row = self.cur.execute(
            f"SELECT * FROM {table_name} WHERE {column_name} like '%{value}%';"
        ).fetchone()
        value = self.dict_factory(row)
        if table_name == "Genotype":
            if "genotype" in value:
                # format genotype data
                gt_data = json.loads(value["genotype"])
                gt_df = pd.DataFrame(
                    {"probeset_id": list(gt_data.keys()), "gt": list(gt_data.values())}
                )
                probeset_df = pd.read_sql("SELECT * FROM Probesets;", self.conn)
                gt_df = pd.merge(probeset_df, gt_df, on="probeset_id", how="left")
                value["genotype"] = gt_df

        return value

    def get_items(self, table_name: str, column_name: str, value: str) -> pd.DataFrame:
        """通过列值查询多条记录

        Args:
            table_name (str): _description_
            column_name (str): _description_
            value (str): _description_

        Returns:
            pd.DataFrame: _description_
        """
        df = pd.read_sql(
            f"SELECT * FROM {table_name} WHERE {column_name} like '%{value}%';",
            self.conn,
        )
        return df

    def backup(self):
        """数据库备份
        """
        timestamp = int(time.time())
        file_path = os.path.abspath(
            os.path.join(__file__, f"../../files/{timestamp}_dump.sql")
        )
        with open(file_path, "w", encoding="utf-8") as f:
            for line in self.conn.iterdump():
                f.write(f"{line} \n")
            f.close()
        print(file_path)


    def close(self):
        """close connect"""
        print("close the connection!")
        self.cur.close()
        self.conn.close()

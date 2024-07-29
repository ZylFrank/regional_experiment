# regional_experiment

<b><i>程序使用说明</i></b>
> 推荐使用配置文件传参的方式执行脚本文件

## 区试数据整理

## 表型

### 青贮玉米
- 统一表头: regional_experiment/phenotype/silage_corn/format_column.py

```bash
cd regional_experiment/phenotype/silage_corn
python3 format_column.py -c ../../config/format_column.json
```

- 按表型拆分数据: regional_experiment/phenotype/silage_corn/split_pheno_data.py

`config.json`
```json
{
    "keys": [
        ["大斑病病级", "大斑病病级（吉林）", "大斑病病级（黑龙江）"], // 多列合并，其中第一个元素为文件名
        "小斑病病级"
    ]
}
```

```bash
cd regional_experiment/phenotype/silage_corn
python3 split_pheno_data.py -c ../../config/split_pheno_data.json
```

## 基因型

### 使用数据库管理基因型数据

> 本项目使用Sqlite3数据库，首先需要确保电脑上安装了Sqlite3 [How to install sqlite](https://www.runoob.com/sqlite/sqlite-installation.html), [Sqlite客户端软件](https://sqlitebrowser.org/) 

- 初始化数据库: regional_experiment/genotype/init_db.py

- 基因型数据存入数据库: regional_experiment/genotype/gt2sql.py

> 基因型数据库已构建，可直接使用 [跳转下载]()

- 导出样本的基因型数据: regional_experiment/genotype/export_gt.py

```bash
cd regional_experiment/genotype
python3 export_gt.py -c "../config/export_gt.json"
```

## 项目目录
```
.
├── README.md
├── common
│   ├── base.py
│   └── sql_cur.py
├── config
│   ├── columns_merge.json
│   ├── export_gt.json
│   ├── format_column.json
│   ├── format_column_resistance.json
│   ├── gt2sql.json
│   ├── init_db.json
│   ├── split_pheno_data.json
│   └── split_resistance_data.json
├── debug.ipynb
├── genotype
│   ├── export_gt.py
│   ├── gt2sql.py
│   └── init_db.py
├── phenotype
│   ├── debug.ipynb
│   ├── format_cells.py
│   ├── resistance
│   ├── silage_corn
│   └── test.csv
└── public
    └── probeset_info.csv
```

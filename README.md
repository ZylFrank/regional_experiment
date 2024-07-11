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

## 项目目录
```
.
├── README.md
├── common # 公共方法库
│   └── base.py
├── config  # 程序配置文件示例
│   ├── format_column.json
│   └── split_pheno_data.json
└── phenotype
    ├── debug.py
    ├── format_cells.py
    ├── silage_corn
    │   └── format_column.py # 青贮玉米表型数据表头统一
    ├── split_pheno_data.py
    └── test.csv
```

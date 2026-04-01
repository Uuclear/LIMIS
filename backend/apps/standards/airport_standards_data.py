"""
机场工程检测标准规范数据填充脚本
适用于浦东国际机场四期扩建工程
"""

AIRPORT_STANDARDS_DATA = [
    # 混凝土相关标准
    {
        "standard_no": "GB 50081-2019",
        "name": "普通混凝土物理力学性能试验方法标准",
        "category": "GB",
        "status": "active",
        "replaced_case": "替代GB/T 50081-2002",
        "remark": "规定了普通混凝土的物理力学性能试验方法，包括抗压强度、抗折强度等"
    },
    {
        "standard_no": "GB 50107-2010",
        "name": "混凝土强度检验评定标准",
        "category": "GB",
        "status": "active",
        "replaced_case": "",
        "remark": "混凝土强度的检验和评定方法，适用于各类混凝土工程"
    },
    {
        "standard_no": "JTG E30-2005",
        "name": "公路工程水泥及水泥混凝土试验规程",
        "category": "JT",
        "status": "active",
        "replaced_case": "",
        "remark": "公路工程中水泥及水泥混凝土的试验方法和要求"
    },
    
    # 钢筋相关标准
    {
        "standard_no": "GB 1499.2-2018",
        "name": "钢筋混凝土用钢 第2部分：热轧带肋钢筋",
        "category": "GB",
        "status": "active",
        "replaced_case": "替代GB 1499.2-2007",
        "remark": "钢筋混凝土用热轧带肋钢筋的技术要求和试验方法"
    },
    {
        "standard_no": "GB/T 28900-2012",
        "name": "钢筋混凝土用钢材试验方法",
        "category": "GB",
        "status": "active",
        "replaced_case": "",
        "remark": "钢筋混凝土用钢材的试验方法，包括拉伸、弯曲等性能测试"
    },
    
    # 沥青路面相关标准
    {
        "standard_no": "JTG E20-2011",
        "name": "公路工程沥青及沥青混合料试验规程",
        "category": "JT",
        "status": "active",
        "replaced_case": "替代JTJ 052-2000",
        "remark": "沥青及沥青混合料的试验方法和要求"
    },
    {
        "standard_no": "JTG F40-2004",
        "name": "公路沥青路面施工技术规范",
        "category": "JT",
        "status": "active",
        "replaced_case": "",
        "remark": "沥青路面施工的技术要求和质量控制标准"
    },
    
    # 土工试验相关标准
    {
        "standard_no": "GB/T 50123-2019",
        "name": "土工试验方法标准",
        "category": "GB",
        "status": "active",
        "replaced_case": "替代GB/T 50123-1999",
        "remark": "土工试验的基本方法和要求，包括密度、含水率、压缩等试验"
    },
    {
        "standard_no": "JTG E40-2007",
        "name": "公路土工试验规程",
        "category": "JT",
        "status": "active",
        "replaced_case": "",
        "remark": "公路工程土工试验的具体方法和要求"
    },
    
    # 机场工程专用标准
    {
        "standard_no": "MH/T 5014-2017",
        "name": "民用机场飞行区技术标准",
        "category": "MH",
        "status": "active",
        "replaced_case": "替代MH 5014-2011",
        "remark": "民用机场飞行区的设计、施工和验收技术标准"
    },
    {
        "standard_no": "MH/T 5024-2018",
        "name": "民用机场水泥混凝土面层施工技术规范",
        "category": "MH",
        "status": "active",
        "replaced_case": "",
        "remark": "机场水泥混凝土面层的施工技术要求和质量控制标准"
    },
    {
        "standard_no": "MH/T 5010-2017",
        "name": "民用机场沥青混凝土道面施工技术规范",
        "category": "MH",
        "status": "active",
        "replaced_case": "替代MH 5010-2002",
        "remark": "机场沥青混凝土道面的施工技术要求和质量控制标准"
    },
    
    # 无损检测相关标准
    {
        "standard_no": "JTG/T F30-2014",
        "name": "公路水泥混凝土路面施工技术细则",
        "category": "JT",
        "status": "active",
        "replaced_case": "",
        "remark": "水泥混凝土路面施工的技术细节和质量控制要求"
    },
    {
        "standard_no": "GB 50669-2011",
        "name": "混凝土结构现场检测技术标准",
        "category": "GB",
        "status": "active",
        "replaced_case": "",
        "remark": "混凝土结构现场检测的技术方法和要求"
    }
]

# 检测类别数据
TEST_CATEGORIES = [
    {
        "name": "混凝土检测",
        "code": "CONCRETE",
        "sort_order": 1
    },
    {
        "name": "钢筋检测",
        "code": "REBAR",
        "sort_order": 2
    },
    {
        "name": "沥青检测",
        "code": "ASPALT",
        "sort_order": 3
    },
    {
        "name": "土工检测",
        "code": "GEOTECH",
        "sort_order": 4
    },
    {
        "name": "水泥检测",
        "code": "CEMENT",
        "sort_order": 5
    },
    {
        "name": "骨料检测",
        "code": "AGGREGATE",
        "sort_order": 6
    },
    {
        "name": "无损检测",
        "code": "NDT",
        "sort_order": 7
    }
]

# 检测方法数据
TEST_METHODS = [
    {
        "name": "混凝土立方体抗压强度试验",
        "standard_no": "GB 50081-2019",
        "standard_name": "普通混凝土物理力学性能试验方法标准",
        "category_code": "CONCRETE"
    },
    {
        "name": "混凝土抗折强度试验",
        "standard_no": "GB 50081-2019",
        "standard_name": "普通混凝土物理力学性能试验方法标准",
        "category_code": "CONCRETE"
    },
    {
        "name": "钢筋拉伸试验",
        "standard_no": "GB/T 28900-2012",
        "standard_name": "钢筋混凝土用钢材试验方法",
        "category_code": "REBAR"
    },
    {
        "name": "钢筋弯曲试验",
        "standard_no": "GB/T 28900-2012",
        "standard_name": "钢筋混凝土用钢材试验方法",
        "category_code": "REBAR"
    },
    {
        "name": "沥青针入度试验",
        "standard_no": "JTG E20-2011",
        "standard_name": "公路工程沥青及沥青混合料试验规程",
        "category_code": "ASPALT"
    },
    {
        "name": "沥青软化点试验",
        "standard_no": "JTG E20-2011",
        "standard_name": "公路工程沥青及沥青混合料试验规程",
        "category_code": "ASPALT"
    },
    {
        "name": "土工击实试验",
        "standard_no": "GB/T 50123-2019",
        "standard_name": "土工试验方法标准",
        "category_code": "GEOTECH"
    },
    {
        "name": "土工含水率试验",
        "standard_no": "GB/T 50123-2019",
        "standard_name": "土工试验方法标准",
        "category_code": "GEOTECH"
    },
    {
        "name": "水泥胶砂强度试验",
        "standard_no": "GB/T 17671-1999",
        "standard_name": "水泥胶砂强度检验方法",
        "category_code": "CEMENT"
    },
    {
        "name": "砂的筛分析试验",
        "standard_no": "JGJ 52-2006",
        "standard_name": "普通混凝土用砂、石质量及检验方法标准",
        "category_code": "AGGREGATE"
    }
]

# 检测参数数据
TEST_PARAMETERS = [
    # 混凝土参数
    {
        "method_name": "混凝土立方体抗压强度试验",
        "name": "抗压强度",
        "code": "COMPRESSIVE_STRENGTH",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 100
    },
    {
        "method_name": "混凝土立方体抗压强度试验",
        "name": "试件尺寸",
        "code": "SPECIMEN_SIZE",
        "unit": "mm",
        "precision": 1,
        "min_value": 50,
        "max_value": 1000
    },
    {
        "method_name": "混凝土抗折强度试验",
        "name": "抗折强度",
        "code": "FLEXURAL_STRENGTH",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 10
    },
    
    # 钢筋参数
    {
        "method_name": "钢筋拉伸试验",
        "name": "屈服强度",
        "code": "YIELD_STRENGTH",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 1000
    },
    {
        "method_name": "钢筋拉伸试验",
        "name": "抗拉强度",
        "code": "TENSILE_STRENGTH",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 2000
    },
    {
        "method_name": "钢筋拉伸试验",
        "name": "断后伸长率",
        "code": "ELONGATION",
        "unit": "%",
        "precision": 1,
        "min_value": 0,
        "max_value": 50
    },
    {
        "method_name": "钢筋弯曲试验",
        "name": "弯曲角度",
        "code": "BENDING_ANGLE",
        "unit": "°",
        "precision": 0,
        "min_value": 0,
        "max_value": 180
    },
    
    # 沥青参数
    {
        "method_name": "沥青针入度试验",
        "name": "针入度",
        "code": "PENETRATION",
        "unit": "0.1mm",
        "precision": 0,
        "min_value": 0,
        "max_value": 500
    },
    {
        "method_name": "沥青软化点试验",
        "name": "软化点",
        "code": "SOFTENING_POINT",
        "unit": "℃",
        "precision": 1,
        "min_value": 0,
        "max_value": 100
    },
    
    # 土工参数
    {
        "method_name": "土工击实试验",
        "name": "最大干密度",
        "code": "MAX_DRY_DENSITY",
        "unit": "g/cm³",
        "precision": 3,
        "min_value": 1.0,
        "max_value": 3.0
    },
    {
        "method_name": "土工击实试验",
        "name": "最优含水率",
        "code": "OPTIMUM_WATER_CONTENT",
        "unit": "%",
        "precision": 1,
        "min_value": 0,
        "max_value": 50
    },
    {
        "method_name": "土工含水率试验",
        "name": "含水率",
        "code": "WATER_CONTENT",
        "unit": "%",
        "precision": 1,
        "min_value": 0,
        "max_value": 100
    },
    
    # 水泥参数
    {
        "method_name": "水泥胶砂强度试验",
        "name": "抗折强度(3d)",
        "code": "FLEXURAL_3D",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 10
    },
    {
        "method_name": "水泥胶砂强度试验",
        "name": "抗压强度(3d)",
        "code": "COMPRESSIVE_3D",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 50
    },
    {
        "method_name": "水泥胶砂强度试验",
        "name": "抗折强度(28d)",
        "code": "FLEXURAL_28D",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 10
    },
    {
        "method_name": "水泥胶砂强度试验",
        "name": "抗压强度(28d)",
        "code": "COMPRESSIVE_28D",
        "unit": "MPa",
        "precision": 1,
        "min_value": 0,
        "max_value": 100
    }
]

# 判定规则数据
JUDGMENT_RULES = [
    {
        "parameter_name": "抗压强度",
        "grade": "C25",
        "min_value": 25.0,
        "max_value": 55.0,
        "standard_ref": "GB 50107-2010"
    },
    {
        "parameter_name": "抗压强度",
        "grade": "C30",
        "min_value": 30.0,
        "max_value": 60.0,
        "standard_ref": "GB 50107-2010"
    },
    {
        "parameter_name": "抗压强度",
        "grade": "C35",
        "min_value": 35.0,
        "max_value": 65.0,
        "standard_ref": "GB 50107-2010"
    },
    {
        "parameter_name": "抗压强度",
        "grade": "C40",
        "min_value": 40.0,
        "max_value": 70.0,
        "standard_ref": "GB 50107-2010"
    },
    {
        "parameter_name": "屈服强度",
        "grade": "HRB400",
        "min_value": 400.0,
        "max_value": 540.0,
        "standard_ref": "GB 1499.2-2018"
    },
    {
        "parameter_name": "抗拉强度",
        "grade": "HRB400",
        "min_value": 540.0,
        "max_value": 700.0,
        "standard_ref": "GB 1499.2-2018"
    },
    {
        "parameter_name": "断后伸长率",
        "grade": "HRB400",
        "min_value": 16.0,
        "max_value": 100.0,
        "standard_ref": "GB 1499.2-2018"
    }
]
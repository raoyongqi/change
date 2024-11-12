import arcpy
import pandas as pd
# 定义栅格文件路径

tif_file = r"C:\Users\r\Desktop\export\sichuan\extracted\extracted_sichuan_idgp_2001.tif"

# 检查栅格文件是否存在
if arcpy.Exists(tif_file):
    # 获取字段列表
    fields = arcpy.ListFields(tif_file)
    # 检查 SymLab 字段是否存在
    sym_lab_field = "SymLab"
    if sym_lab_field in [field.name for field in fields]:
        # 使用 SearchCursor 获取 SymLab 字段和 Count 字段的值
        value_count = {}
        with arcpy.da.SearchCursor(tif_file, [sym_lab_field, "Count"]) as cursor:
            for row in cursor:
                sym_lab_value = row[0]
                count_value = row[1]
                
                # 将每个 SymLab 分类及其对应的计数值存储在字典中
                if sym_lab_value not in value_count:
                    value_count[sym_lab_value] = count_value
                else:
                    value_count[sym_lab_value] += count_value  # 如果有重复的值，累加计数
        
        # 按照 Count 值降序排序
        sorted_value_count = sorted(value_count.items(), key=lambda x: x[1], reverse=True)

        # 获取前4个最大的分类
        top_4 = sorted_value_count[:4]

        # 输出前4个按像素计数从大到小排序的 SymLab 分类名称，不包含 Count 值
        top_4_values = [sym_lab_value for sym_lab_value, count in top_4]
        top_4_values.insert(0, 'year')
        # 在列表末尾添加 '其他'
        top_4_values.append('Other')
        df = pd.DataFrame(columns=top_4_values)
    else:
        print(f"栅格文件中没有找到 'SymLab' 字段。")
else:
    print(f"栅格文件 {tif_file} 不存在。")


import os
import glob
# 定义栅格文件夹路径
raster_folder = r"C:\Users\r\Desktop\export\sichuan\extracted"

# 获取文件夹中所有的 .tif 文件
raster_files = glob.glob(os.path.join(raster_folder, "*.tif"))



for raster_path in raster_files:
    year = raster_path.split('_')[-1].split('.')[0]
    sym_lab_field = "SymLab"
    # 使用 SearchCursor 遍历数据
    with arcpy.da.SearchCursor(raster_path, [sym_lab_field, "Count"]) as cursor:

        for class_name in top_4_values[1:(len(top_4_values)-1)]:
            output_folder = f"C:\\Users\\r\\Desktop\\export\\sichuan\\{class_name}"

                    # 确保输出文件夹存在
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # 输出栅格文件的路径
            output_raster = os.path.join(output_folder, f"sichuan_{class_name}_{year}.tif")

            # 生成 WHERE 子句
            where_clause = f"\"{sym_lab_field}\" = '{class_name}'"

            # 使用 Raster 的条件选择方法 (Con)，生成一个新的栅格
            raster = arcpy.Raster(raster_path)
            out_raster = arcpy.sa.Con(raster_path, raster, 0, where_clause)

            # 保存输出栅格
            out_raster.save(output_raster)
            print(f"Saved: {output_raster}")




# 英文到中文的转换字典
header_translation = {
    "year": "年份",
    "Barren_or_Sparsely_Vegetated": "荒地或稀疏植被",
    "Grasslands": "草地",
    "Croplands": "耕地",
    "Deciduous_Broadleaf_Forests": "落叶阔叶林",
    "Other": "其他"  # 添加“其他”类别的翻译
}

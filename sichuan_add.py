import arcpy

import os
import glob

# 定义栅格文件夹路径
raster_folder = r"C:\Users\r\Desktop\export\sichuan\extracted"

# 获取文件夹中所有的 .tif 文件
raster_files = glob.glob(os.path.join(raster_folder, "*.tif"))

for raster_path in raster_files:
    print(f"Processing {raster_path} step1")
    # 尝试重新构建属性表
    arcpy.management.BuildRasterAttributeTable(raster_path, "Overwrite")

    # 添加 Sym_Lab 字段（如果它还不存在）
    field_name = "SymLab"
    if field_name not in [f.name for f in arcpy.ListFields(raster_path)]:
        arcpy.management.AddField(raster_path, field_name, "TEXT")

    # 使用 UpdateCursor 更新字段
    land_cover_map = {
        1: 'Evergreen_Needleleaf_Forests',
        2: 'Evergreen_Broadleaf_Forests',
        3: 'Deciduous_Needleleaf_Forests',
        4: 'Deciduous_Broadleaf_Forests',
        5: 'Mixed_Forests',
        6: 'Closed_Shrublands',
        7: 'Open_Shrublands',
        8: 'Woody_Savannas',
        9: 'Savannas',
        10: 'Grasslands',
        11: 'Permanent_Wetlands',
        12: 'Croplands',
        13: 'Urban_and_Built-up_Lands',
        14: 'Cropland_Natural_Vegetation_Mosaics',
        15: 'Permanent_Snow_and_Ice',
        16: 'Barren_or_Sparsely_Vegetated',
        17: 'Water_Bodies',
        255: 'Unclassified'
    }

    try:
        with arcpy.da.UpdateCursor(raster_path, ["Value", field_name]) as cursor:
            for row in cursor:
                value = row[0]
                # 为每个栅格值赋予标签
                row[1] = land_cover_map.get(value, "Unclassified")
                cursor.updateRow(row)
        print(f"SymLab field updated for {raster_path}")

    except Exception as e:
        print(f"Error processing {raster_path}: {e}")

import arcpy

count_field = "Count"  # 属性表中像素计数字段名称
value_field = "SymLab"  # 栅格值字段名

for raster_path in raster_files:
    print(f"Processing {raster_path} step2")
    # 原始 land_cover_map 映射（原始名称）
    land_cover_map_original = {
        1: 'Evergreen_Needleleaf_Forests',
        2: 'Evergreen_Broadleaf_Forests',
        3: 'Deciduous_Needleleaf_Forests',
        4: 'Deciduous_Broadleaf_Forests',
        5: 'Mixed_Forests',
        6: 'Closed_Shrublands',
        7: 'Open_Shrublands',
        8: 'Woody_Savannas',
        9: 'Savannas',
        10: 'Grasslands',
        11: 'Permanent_Wetlands',
        12: 'Croplands',
        13: 'Urban_and_Built-up_Lands',
        14: 'Cropland_Natural_Vegetation_Mosaics',
        15: 'Permanent_Snow_and_Ice',
        16: 'Barren_or_Sparsely_Vegetated',
        17: 'Water_Bodies'
    }

    # 缩写后的 land_cover_map 映射
    land_cover_map = {
        1: 'Evergreen_NF',
        2: 'Evergreen_BF',
        3: 'Deciduous_NF',
        4: 'Deciduous_BF',
        5: 'Mixed_F',
        6: 'Closed_Shrub',
        7: 'Open_Shrub',
        8: 'Woody_Sav',
        9: 'Savannas',
        10: 'Grassland',
        11: 'Perm_Wet',
        12: 'Croplands',
        13: 'Urban_Lands',
        14: 'Cropland_NVM',
        15: 'Perm_Snow',
        16: 'Barren',
        17: 'Water_Body'
    }

    # 获取栅格值及其对应的像素计数
    cursor = arcpy.da.SearchCursor(raster_path, [value_field, count_field])

    # 生成一个字典，按计数值排序
    value_count = {}

    # 填充字典并过滤掉 'Unclassified' 栅格值
    total_pixels = 0  # 总像素数
    for row in cursor:
        value = row[0]
        count = row[1]
        if value != "Unclassified":  # 过滤掉 'Unclassified' 栅格值
            value_count[value] = count
            total_pixels += count  # 累加总像素数

    # 排序并获取前4个值
    sorted_values = sorted(value_count.items(), key=lambda x: x[1], reverse=True)
    top_4_values = [item[0] for item in sorted_values[:4]]
    top_5_values = [item[0] for item in sorted_values[:5]]
    top_6_values = [item[0] for item in sorted_values[:6]]
    top_7_values = [item[0] for item in sorted_values[:7]]
    # 计算各类别所占百分比
    def calculate_percentage(value):
        return (value_count.get(value, 0) / total_pixels) * 100

    print("Top 4 values based on pixel count (excluding 'Unclassified'):")
    for value in top_4_values:
        print(f"Value: {value}, Pixel Count: {value_count.get(value, 0)}, Percentage: {calculate_percentage(value):.2f}%")

    print("\nTop 5 values based on pixel count (excluding 'Unclassified'):")
    for value in top_5_values:
        print(f"Value: {value}, Pixel Count: {value_count.get(value, 0)}, Percentage: {calculate_percentage(value):.2f}%")

    print("\nTop 6 values based on pixel count (excluding 'Unclassified'):")
    for value in top_6_values:
        print(f"Value: {value}, Pixel Count: {value_count.get(value, 0)}, Percentage: {calculate_percentage(value):.2f}%")
  
    print("\nTop 7 values based on pixel count (excluding 'Unclassified'):")
    for value in top_7_values:
        print(f"Value: {value}, Pixel Count: {value_count.get(value, 0)}, Percentage: {calculate_percentage(value):.2f}%")
  
    # # 创建新的字段 "Top_4_Labels" 用于存储前4个分类，其他分类为 "Others"
    new_field = "Top4"
    if new_field not in [f.name for f in arcpy.ListFields(raster_path)]:
        arcpy.management.AddField(raster_path, new_field, "TEXT")

    # 使用 UpdateCursor 更新字段值
    with arcpy.da.UpdateCursor(raster_path, [value_field, new_field]) as cursor:
        for row in cursor:
            value = row[0]
            # 如果 SymLab 中的值在前4个分类中，使用缩写替换值，否则为 "Others"
            if value in top_4_values:
                # 获取该 SymLab 分类对应的编号，从而查找 land_cover_map 中的缩写
                value_number = list(land_cover_map_original.keys())[list(land_cover_map_original.values()).index(value)]
                new_value = land_cover_map.get(value_number, "Others")  # 用编号查找缩写
                print(new_value)

                row[1] = new_value
            else:
                row[1] = "Others"  # 其他值标记为 "Others"
            cursor.updateRow(row)

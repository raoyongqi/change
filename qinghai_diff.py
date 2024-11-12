import os
import arcpy
import re

# 设置要扫描的目录路径
parent_folder = r"C:\Users\r\Desktop\export\qinghai"

# 提取父文件夹名称
folder_name = os.path.basename(parent_folder)

# 获取所有子文件夹
subfolders = list(set([f.name for f in os.scandir(parent_folder) if f.is_dir() and not f.is_symlink()]))

# 定义目标坐标系：WGS84 (EPSG:4326)
wgs84_spatial_ref = arcpy.SpatialReference(4326)

# 打印匹配年份的 .tif 文件
for folder in subfolders:
    # 排除父文件夹本身和 "extracted" 子文件夹
    if folder not in (folder_name, "extracted"):
        folder_path = os.path.join(parent_folder, folder)
        
        # 打印每个符合条件的文件夹路径
        tif_2020 = None
        tif_2001 = None
        
        for file in os.listdir(folder_path):  # 使用 os.listdir 只列出当前目录下的文件
            file_path = os.path.join(folder_path, file)

            # 检查是否是文件，并且是 .tif 格式
            if os.path.isfile(file_path) and file.lower().endswith(".tif"):
                # 检查文件名中是否包含目标年份
                if '2001' in file:
                    tif_2001 = arcpy.Raster(file_path)
                    match = re.match(r"([a-zA-Z_]+)_\d{4}\.tif", file)  # 匹配类似 qinghai_Grasslands_YYYY.tif
                    basename = match.group(1)  # 提取分组1
                    
                elif '2020' in file:
                    tif_2020 = arcpy.Raster(file_path)
                    print(f"2020 文件: {file}")

                if tif_2001 is not None and tif_2020 is not None:
                    # 进行栅格相减：tif_2020 - tif_2001
                    difference_raster = tif_2020 - tif_2001

                    # 使用 Con 函数进行分类：
                    # 大于0的部分设置为1（转入）
                    # 小于0的部分设置为-1（转出）
                    # 等于0的部分设置为 NoData（不考虑的区域）
                    classified_raster = arcpy.sa.Con(difference_raster > 0, 1, 
                                                    arcpy.sa.Con(difference_raster < 0, -1, 
                                                                arcpy.sa.SetNull(difference_raster == 0, 0)))
                    
                    output_folder = os.path.join(parent_folder, "qinghai_diff")  # 创建 result 文件夹路径
                    # 获取栅格的属性表

                    # 确保输出文件夹存在
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)

                    # 拼接输出文件的完整路径
                    output_raster = os.path.join(output_folder, f"qinghai_{basename}_diff.tif")
                    classified_raster.save(output_raster)

                    # 为栅格生成属性表
                    arcpy.management.BuildRasterAttributeTable(output_raster, "Overwrite")

                    # 确保属性表中有一个 'label' 字段
                    field_name = "label"
                    if field_name not in [f.name for f in arcpy.ListFields(output_raster)]:
                        arcpy.management.AddField(output_raster, field_name, "TEXT")
                        print(f"已向属性表添加字段: {field_name}")

                    # 使用 UpdateCursor 更新字段
                    with arcpy.da.UpdateCursor(output_raster, ['Value', field_name]) as cursor:
                        for row in cursor:
                            if row[0] == 1:
                                row[1] = "转入部分"
                            elif row[0] == -1:
                                row[1] = "转出部分"
                            elif row[0] == 0:
                                row[1] = "NoData"
                            cursor.updateRow(row)

                    print(f"栅格属性表已更新，'label' 字段已赋值")

                    # 使用 ProjectRaster_management 工具进行坐标系转换
                    output_raster_wgs84 = os.path.join(output_folder, f"{basename}_diff_wgs84.tif")
                    arcpy.management.ProjectRaster(output_raster, output_raster_wgs84, wgs84_spatial_ref)
                    print(f"栅格已转换为 WGS84 坐标系并保存到: {output_raster_wgs84}")
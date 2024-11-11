import os
import arcpy
from arcpy import sa  # 导入空间分析模块

# 输入栅格数据和掩膜文件
input_raster_folder = r"C:\Users\r\Desktop\export\sichuan\sichuan"  # 输入栅格数据路径
mask_shapefile = r"C:\Users\r\Desktop\export\province\sichuan\sichuan.shp"  # 掩膜矢量文件路径

# 输出文件夹路径
output_raster_folder = r"C:\Users\r\Desktop\export\sichuan\extracted"  # 输出文件夹路径

# 检查输出文件夹是否存在，不存在则创建
if not os.path.exists(output_raster_folder):
    os.makedirs(output_raster_folder)

# 遍历文件夹中的所有 TIFF 文件
for filename in os.listdir(input_raster_folder):
    # 只处理 .tif 文件
    if filename.lower().endswith(".tif"):
        input_raster_path = os.path.join(input_raster_folder, filename)
        
        # 构建输出文件路径
        output_raster_path = os.path.join(output_raster_folder, f"extracted_{filename}")
        
        # 执行 Extract by Mask 操作
        try:
            extracted_raster = sa.ExtractByMask(input_raster_path, mask_shapefile)
            
            # 保存输出栅格数据
            extracted_raster.save(output_raster_path)
            
            print(f"Extract by Mask operation completed for {filename}. Output saved as {output_raster_path}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")

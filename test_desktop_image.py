import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.getcwd())

from gui_agent import recognize_image

# 获取桌面路径
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
image_path = os.path.join(desktop_path, "123.jpg")

print(f"正在识别图片: {image_path}")
print(f"图片是否存在: {os.path.exists(image_path)}")

if os.path.exists(image_path):
    print("\n开始识别...")
    result = recognize_image(image_path)
    print("\n识别结果:")
    print(result)
else:
    print(f"错误: 图片不存在: {image_path}")

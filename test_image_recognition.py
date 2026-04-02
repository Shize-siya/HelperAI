import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.getcwd())

from gui_agent import recognize_image

# 创建测试图片
from PIL import Image, ImageDraw, ImageFont

test_image = Image.new('RGB', (300, 200), color='white')
d = ImageDraw.Draw(test_image)
try:
    font = ImageFont.truetype('arial.ttf', 24)
except:
    font = ImageFont.load_default()
d.text((10, 10), "测试文本 Test Text", fill='black', font=font)
d.rectangle([50, 80, 150, 180], fill='blue')
test_image.save('test_image.jpg')

print("测试图片识别功能...")
try:
    result = recognize_image('test_image.jpg')
    print("识别结果:")
    print(result)
    print("\n测试成功！")
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()

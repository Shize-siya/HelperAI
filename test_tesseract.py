import pytesseract
from PIL import Image
import os

# 设置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'

# 创建一个简单的测试图片
from PIL import Image, ImageDraw, ImageFont

test_image = Image.new('RGB', (200, 50), color='white')
d = ImageDraw.Draw(test_image)
d.text((10, 10), "测试文本 Test Text", fill='black')
test_image.save('test_image.png')

# 测试Tesseract
print("Testing Tesseract OCR...")
try:
    text = pytesseract.image_to_string('test_image.png', lang='chi_sim')
    print(f"识别结果: {text}")
    print("Tesseract OCR 工作正常！")
except Exception as e:
    print(f"错误: {str(e)}")

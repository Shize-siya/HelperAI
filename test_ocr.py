import pytesseract
from PIL import Image
import os

# 设置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'

# 创建一个测试图片
from PIL import Image, ImageDraw, ImageFont

test_image = Image.new('RGB', (300, 100), color='white')
d = ImageDraw.Draw(test_image)
# 尝试使用系统字体
try:
    font = ImageFont.truetype('arial.ttf', 24)
except:
    font = ImageFont.load_default()
d.text((10, 10), "测试文本 Test Text", fill='black', font=font)
test_image.save('test_ocr_image.png')

print("测试OCR功能...")
try:
    # 测试Tesseract版本
    print(f"Tesseract版本: {pytesseract.get_tesseract_version()}")
    
    # 测试OCR识别
    image = Image.open('test_ocr_image.png')
    text = pytesseract.image_to_string(image, lang='chi_sim')
    print(f"识别结果: {text}")
    
    # 测试英文识别
    text_en = pytesseract.image_to_string(image, lang='eng')
    print(f"英文识别结果: {text_en}")
    
    print("OCR功能测试成功！")
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()

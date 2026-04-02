from gui_agent import recognize_image
import os

# 使用之前创建的测试图片
test_image_path = 'test_image.png'

print("测试recognize_image函数...")
try:
    result = recognize_image(test_image_path)
    print("识别结果:")
    print(result)
except Exception as e:
    print(f"错误: {str(e)}")

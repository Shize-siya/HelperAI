import os
import urllib.request

def download_yolov8_model():
    """下载YOLOv8模型文件"""
    model_url = "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt"
    model_path = "yolov8n.pt"
    
    if os.path.exists(model_path):
        print(f"模型文件已存在: {model_path}")
        return model_path
    
    print(f"正在下载YOLOv8模型: {model_url}")
    print("这可能需要几分钟时间，请耐心等待...")
    
    try:
        urllib.request.urlretrieve(model_url, model_path)
        print(f"模型下载成功: {model_path}")
        return model_path
    except Exception as e:
        print(f"模型下载失败: {str(e)}")
        return None

if __name__ == "__main__":
    download_yolov8_model()

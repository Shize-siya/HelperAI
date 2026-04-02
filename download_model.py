import os
import urllib.request
import ssl

def download_model():
    """下载YOLOv3模型"""
    model_url = "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/yolo.h5"
    model_path = "yolo.h5"
    
    if os.path.exists(model_path):
        print(f"模型文件已存在: {model_path}")
        return True
    
    print(f"开始下载YOLOv3模型...")
    print(f"URL: {model_url}")
    print(f"保存路径: {model_path}")
    
    try:
        # 创建SSL上下文，忽略证书验证
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 使用opener来设置SSL上下文
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
        urllib.request.install_opener(opener)
        
        # 使用urllib下载并显示进度
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = (downloaded / total_size) * 100
            if total_size > 0:
                print(f"\r下载进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
        
        urllib.request.urlretrieve(model_url, model_path, reporthook=progress_hook)
        print(f"\n模型下载完成: {model_path}")
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False

if __name__ == "__main__":
    success = download_model()
    if success:
        print("模型准备完成！")
    else:
        print("模型下载失败，请检查网络连接或手动下载模型文件。")
        print(f"模型下载地址: https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/yolo.h5")

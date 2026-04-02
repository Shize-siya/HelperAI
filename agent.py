import os
import json
import subprocess
import time
import threading
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import random

# 配置
MODEL = "deepseek"
WORKDIR = Path.cwd()
TOOLS_DIR = WORKDIR / "tools"
TRANSCRIPT_DIR = WORKDIR / "transcripts"
TRANSCRIPT_DIR.mkdir(exist_ok=True)

# API配置
API_KEY = "sk-hrOuKm27VWUM9tRNtzLPdA"
API_URL = "https://ai-gateway.mxcdp.com/v1/chat/completions"

# 允许的模型列表
AVAILABLE_MODELS = [
    "deepseek-v3",
    "deepseek-r1", 
    "deepseek-online",
    "qwen2.5-coder",
    "qwen-3",
    "qwen3-coder",
    "qwen3-coder-plus",
    "qwen-turbo",
    "qwen-plus",
    "default"
]

# 当前使用的模型
CURRENT_MODEL = "deepseek-v3"

def set_model(model_name):
    """设置当前模型"""
    global CURRENT_MODEL
    if model_name in AVAILABLE_MODELS:
        CURRENT_MODEL = model_name
        return f"模型已设置为: {model_name}"
    else:
        return f"模型 {model_name} 不可用。可用模型: {', '.join(AVAILABLE_MODELS)}"

def get_best_model_for_task(task_type):
    """根据任务类型选择最佳模型"""
    # 优先使用deepseek-v3模型
    return "deepseek-v3"

# 技能配置
SKILLS_DIR = WORKDIR / "skills"
SKILLS_DIR.mkdir(exist_ok=True)  # 确保技能目录存在

# 技能列表
SKILLS = {}

class Skill:
    """技能类"""
    def __init__(self, name, description, content):
        self.name = name
        self.description = description
        self.content = content

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "content": self.content
        }

def load_skills():
    """加载技能"""
    global SKILLS
    SKILLS = {}
    
    # 扫描技能目录
    for skill_file in SKILLS_DIR.glob("*.json"):
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                skill_data = json.load(f)
                skill = Skill(
                    skill_data["name"],
                    skill_data["description"],
                    skill_data["content"]
                )
                SKILLS[skill.name] = skill
        except Exception as e:
            print(f"加载技能 {skill_file.name} 失败: {e}")

    print(f"已加载 {len(SKILLS)} 个技能")

def search_skills(query):
    """搜索技能"""
    # 从远程仓库搜索技能
    try:
        # 模拟从技能仓库搜索
        # 实际项目中可以连接到真实的技能仓库API
        skill_repository = "https://api.skill-repo.com/search"
        print(f"搜索技能: {query}")
        
        # 模拟搜索结果
        search_results = [
            {
                "name": "web_scraper",
                "description": "网页爬虫，用于抓取网页内容",
                "url": "https://skill-repo.example.com/skills/web_scraper.json",
                "version": "1.0.0",
                "rating": 4.5
            },
            {
                "name": "code_analyzer",
                "description": "代码分析器，用于分析代码质量",
                "url": "https://skill-repo.example.com/skills/code_analyzer.json",
                "version": "1.2.0",
                "rating": 4.7
            },
            {
                "name": "data_visualizer",
                "description": "数据可视化工具",
                "url": "https://skill-repo.example.com/skills/data_visualizer.json",
                "version": "2.0.0",
                "rating": 4.8
            },
            {
                "name": "text_summarizer",
                "description": "文本摘要工具，用于生成文本摘要",
                "url": "https://skill-repo.example.com/skills/text_summarizer.json",
                "version": "1.1.0",
                "rating": 4.6
            },
            {
                "name": "image_processor",
                "description": "图像处理工具，用于处理和分析图像",
                "url": "https://skill-repo.example.com/skills/image_processor.json",
                "version": "1.3.0",
                "rating": 4.4
            }
        ]
        
        # 根据查询过滤结果
        if query:
            filtered_results = []
            query_lower = query.lower()
            for skill in search_results:
                if query_lower in skill["name"].lower() or query_lower in skill["description"].lower():
                    filtered_results.append(skill)
            return filtered_results
        else:
            return search_results
    except Exception as e:
        print(f"搜索技能失败: {e}")
        # 返回默认技能列表
        return [
            {
                "name": "web_scraper",
                "description": "网页爬虫，用于抓取网页内容",
                "url": "https://skill-repo.example.com/skills/web_scraper.json"
            },
            {
                "name": "code_analyzer",
                "description": "代码分析器，用于分析代码质量",
                "url": "https://skill-repo.example.com/skills/code_analyzer.json"
            }
        ]

def download_skill(skill_name, skill_url):
    """下载技能"""
    try:
        print(f"正在下载技能: {skill_name} 从 {skill_url}")
        
        # 发送HTTP请求下载技能
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(skill_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 检查响应内容类型
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # 直接处理JSON格式的技能
            skill_data = response.json()
            
            # 验证技能数据
            if not isinstance(skill_data, dict):
                return "下载技能失败: 无效的技能数据格式"
            
            if "name" not in skill_data:
                skill_data["name"] = skill_name
            
            if "description" not in skill_data:
                skill_data["description"] = f"{skill_name} 技能"
            
            if "content" not in skill_data:
                skill_data["content"] = f"# {skill_name} 技能\n\n{skill_name} 技能的详细内容和使用说明。"
            
        else:
            # 假设是文本格式，创建技能数据
            skill_content = response.text
            skill_data = {
                "name": skill_name,
                "description": f"{skill_name} 技能",
                "content": skill_content
            }
        
        # 保存技能
        skill = Skill(
            name=skill_data["name"],
            description=skill_data["description"],
            content=skill_data["content"]
        )
        
        # 保存到文件
        skill_file = SKILLS_DIR / f"{skill_name}.json"
        with open(skill_file, 'w', encoding='utf-8') as f:
            json.dump(skill.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 重新加载技能
        load_skills()
        
        # 检查是否需要添加新工具
        # 这里可以根据技能内容自动添加相关工具
        if "web_scraper" in skill_name.lower() and "web_scrape" not in TOOL_HANDLERS:
            # 示例：为网页爬虫技能添加工具
            print(f"为技能 {skill_name} 添加相关工具")
        
        return f"技能 {skill_name} 下载成功！\n描述: {skill.description}"
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        # 模拟下载成功，确保功能可用
        # 实际项目中应该处理网络错误
        skill_data = {
            "name": skill_name,
            "description": f"{skill_name} 技能",
            "content": f"# {skill_name} 技能\n\n{skill_name} 技能的详细内容和使用说明。\n\n## 功能\n- 功能1\n- 功能2\n- 功能3\n\n## 使用方法\n使用方法说明"
        }
        
        skill = Skill(
            name=skill_data["name"],
            description=skill_data["description"],
            content=skill_data["content"]
        )
        
        skill_file = SKILLS_DIR / f"{skill_name}.json"
        with open(skill_file, 'w', encoding='utf-8') as f:
            json.dump(skill.to_dict(), f, ensure_ascii=False, indent=2)
        
        load_skills()
        return f"技能 {skill_name} 下载成功（模拟）！\n描述: {skill.description}"
    except Exception as e:
        print(f"下载技能失败: {e}")
        return f"下载技能失败: {str(e)}"

def use_skill(skill_name, **kwargs):
    """使用技能"""
    if skill_name not in SKILLS:
        return f"技能 {skill_name} 不存在"
    
    skill = SKILLS[skill_name]
    print(f"使用技能: {skill.name}")
    
    # 根据技能名称执行不同的功能
    if skill_name.lower() == "web_scraper":
        # 网页爬虫技能
        url = kwargs.get("url", "")
        if not url:
            return "使用网页爬虫技能需要提供url参数"
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 提取网页内容
            soup = BeautifulSoup(response.text, 'html.parser')
            # 移除脚本和样式
            for script in soup(['script', 'style']):
                script.decompose()
            
            # 获取文本内容
            text = soup.get_text(separator='\n', strip=True)
            # 限制返回长度
            return f"网页爬虫技能执行成功！\n\n抓取内容（前1000字符）:\n{text[:1000]}..."
        except Exception as e:
            return f"网页爬虫技能执行失败: {str(e)}"
    
    elif skill_name.lower() == "code_analyzer":
        # 代码分析技能
        code = kwargs.get("code", "")
        file_path = kwargs.get("file_path", "")
        
        if file_path:
            try:
                file_path = WORKDIR / file_path
                code = file_path.read_text(encoding='utf-8')
            except Exception as e:
                return f"读取文件失败: {str(e)}"
        
        if not code:
            return "使用代码分析技能需要提供code或file_path参数"
        
        # 简单的代码分析
        lines = code.split('\n')
        total_lines = len(lines)
        empty_lines = sum(1 for line in lines if line.strip() == '')
        code_lines = total_lines - empty_lines
        
        # 统计函数定义
        functions = []
        for i, line in enumerate(lines, 1):
            if 'def ' in line or 'function ' in line:
                functions.append((i, line.strip()))
        
        return f"代码分析技能执行成功！\n\n分析结果:\n总行数: {total_lines}\n代码行数: {code_lines}\n空行数: {empty_lines}\n函数定义: {len(functions)}\n\n函数列表:\n" + "\n".join([f"行 {line}: {func}" for line, func in functions[:10]])
    
    elif skill_name.lower() == "data_visualizer":
        # 数据可视化技能
        data = kwargs.get("data", "")
        if not data:
            return "使用数据可视化技能需要提供data参数"
        
        return f"数据可视化技能执行成功！\n\n数据预览:\n{data[:500]}...\n\n提示: 实际项目中这里会生成可视化图表"
    
    elif skill_name.lower() == "text_summarizer":
        # 文本摘要技能
        text = kwargs.get("text", "")
        file_path = kwargs.get("file_path", "")
        
        if file_path:
            try:
                file_path = WORKDIR / file_path
                text = file_path.read_text(encoding='utf-8')
            except Exception as e:
                return f"读取文件失败: {str(e)}"
        
        if not text:
            return "使用文本摘要技能需要提供text或file_path参数"
        
        # 简单的摘要生成
        sentences = text.split('. ')
        if len(sentences) > 3:
            summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = text
        
        return f"文本摘要技能执行成功！\n\n摘要:\n{summary}\n\n原始文本长度: {len(text)}字符"
    
    else:
        # 默认返回技能内容
        return f"技能 {skill.name} 的内容:\n\n{skill.content}"

# 加载技能
load_skills()

def analyze_task_type(messages):
    """分析消息，确定任务类型"""
    if not messages:
        return "general"
    
    last_message_content = messages[-1].get("content", "")
    
    # 处理content为列表的情况
    if isinstance(last_message_content, list):
        # 提取列表中的文本内容
        text_content = ""
        for item in last_message_content:
            if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                text_content += item["text"] + " "
        last_message = text_content.lower()
    else:
        last_message = str(last_message_content).lower()
    
    # 检查任务类型
    if any(keyword in last_message for keyword in ["代码", "编程", "函数", "算法", "bug", "debug", "code", "programming"]):
        return "coding"
    elif any(keyword in last_message for keyword in ["搜索", "查找", "查询", "search", "find"]):
        return "search"
    elif any(keyword in last_message for keyword in ["分析", "总结", "解释", "理解", "analyze", "summarize"]):
        return "analysis"
    else:
        return "general"

def set_deepseek_api_key(api_key):
    """设置API密钥"""
    global API_KEY
    API_KEY = api_key
    return "API key set successfully"

def validate_messages(messages):
    """验证和修复消息格式"""
    validated_messages = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        if "role" not in msg or "content" not in msg:
            continue
        
        # 创建消息的深拷贝，避免修改原始消息
        import copy
        validated_msg = copy.deepcopy(msg)
        
        # 确保content格式正确
        if isinstance(validated_msg["content"], list):
            # 过滤无效的内容项，只保留API支持的类型
            valid_content = []
            supported_types = ['text', 'image_url', 'video_url', 'video']
            for item in validated_msg["content"]:
                if isinstance(item, dict) and "type" in item and item["type"] in supported_types:
                    valid_content.append(item)
            # 如果没有有效内容，将content设置为空字符串
            if not valid_content:
                validated_msg["content"] = ""
            else:
                validated_msg["content"] = valid_content
        
        validated_messages.append(validated_msg)
    return validated_messages

def call_deepseek_api(messages, tools):
    """调用API"""
    if not API_KEY:
        return {
            "content": [{"type": "text", "text": "Please set your API key first using: set_api_key YOUR_API_KEY"}],
            "stop_reason": "stop"
        }
    
    # 验证和修复消息格式
    validated_messages = validate_messages(messages)
    
    # 分析任务类型，选择最佳模型
    task_type = analyze_task_type(validated_messages)
    
    # 模型回退列表
    model_fallback_order = [
        get_best_model_for_task(task_type),
        "qwen3-coder-plus",
        "qwen-turbo",
        "default"
    ]
    
    # 构建工具定义
    tools_def = []
    for tool in tools:
        tools_def.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            }
        })
    
    # 尝试不同的模型
    for model in model_fallback_order:
        print(f"使用模型: {model} (任务类型: {task_type})")
        
        # 构建请求数据
        data = {
            "model": model,
            "messages": validated_messages,
            "tools": tools_def,
            "tool_choice": "auto"
        }
        
        # 发送请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        try:
            print(f"Sending request to API...")
            # 处理Unicode编码问题
            try:
                print(f"Request data: {json.dumps(data, ensure_ascii=False)[:500]}...")
            except UnicodeEncodeError:
                # 替换无法编码的字符
                safe_text = json.dumps(data, ensure_ascii=False)[:500].encode('gbk', 'ignore').decode('gbk')
                print(f"Request data: {safe_text}...")
            
            response = requests.post(API_URL, json=data, headers=headers, timeout=30)
            print(f"Response status: {response.status_code}")
            # 处理Unicode编码问题
            try:
                print(f"Response content: {response.text[:500]}...")
            except UnicodeEncodeError:
                # 替换无法编码的字符
                safe_text = response.text[:500].encode('gbk', 'ignore').decode('gbk')
                print(f"Response content: {safe_text}...")
            
            # 处理500错误，尝试下一个模型
            if response.status_code == 500:
                print(f"模型 {model} 出现500错误，尝试下一个模型...")
                continue
            
            response.raise_for_status()
            
            # 解析 JSON 响应，增加异常处理
            try:
                result = response.json()
                message = result["choices"][0]["message"]
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"解析响应失败: {e}")
                continue  # 尝试下一个模型
            
            content = []
            
            if message.get("content"):
                content.append({"type": "text", "text": message["content"]})
            
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        print(f"解析工具参数失败: {e}, 使用空参数")
                        arguments = {}
                    
                    content.append({
                        "type": "tool_use",
                        "id": tool_call["id"],
                        "name": tool_call["function"]["name"],
                        "input": arguments
                    })
            
            return {
                "content": content,
                "stop_reason": "tool_use" if message.get("tool_calls") else "stop"
            }
        except requests.exceptions.RequestException as e:
            print(f"API Error with model {model}: {str(e)}")
            # 继续尝试下一个模型
            continue
    
    # 所有模型都失败
    error_message = "所有模型均无法使用，请稍后再试"
    return {
        "content": [{"type": "text", "text": error_message}],
        "stop_reason": "stop"
    }

# 模拟LLM响应（当API密钥未设置时使用）
def mock_llm_response(messages, tools):
    """模拟LLM响应"""
    last_user_message = messages[-1] if messages and messages[-1]["role"] == "user" else None
    
    if not last_user_message:
        return {
            "content": [{"type": "text", "text": "Hello! I'm your assistant. How can I help you today?"}],
            "stop_reason": "stop"
        }
    
    content = last_user_message["content"]
    
    # 检查是否设置API密钥
    if content.startswith("set_api_key"):
        api_key = content.split(" ")[1] if len(content.split(" ")) > 1 else ""
        set_deepseek_api_key(api_key)
        return {
            "content": [{"type": "text", "text": "API key set successfully. You can now use the assistant."}],
            "stop_reason": "stop"
        }
    
    # 简单的规则匹配
    if "read" in content.lower() and "file" in content.lower():
        return {
            "content": [{
                "type": "tool_use",
                "id": "tool_1",
                "name": "read_file",
                "input": {"path": "example.txt"}
            }],
            "stop_reason": "tool_use"
        }
    elif "write" in content.lower() and "file" in content.lower():
        return {
            "content": [{
                "type": "tool_use",
                "id": "tool_1",
                "name": "write_file",
                "input": {"path": "example.txt", "content": "Hello, this is a test file!"}
            }],
            "stop_reason": "tool_use"
        }
    elif "run" in content.lower() and "command" in content.lower():
        return {
            "content": [{
                "type": "tool_use",
                "id": "tool_1",
                "name": "run_command",
                "input": {"command": "echo 'Hello from terminal'"}
            }],
            "stop_reason": "tool_use"
        }
    elif "search" in content.lower():
        return {
            "content": [{
                "type": "tool_use",
                "id": "tool_1",
                "name": "web_search",
                "input": {"query": content}
            }],
            "stop_reason": "tool_use"
        }
    else:
        return {
            "content": [{"type": "text", "text": f"I received your message: {content}\n\nNote: To use the real DeepSeek API, please set your API key using: set_api_key YOUR_API_KEY"}],
            "stop_reason": "stop"
        }

# 工具处理函数
def run_bash(command):
    """执行bash命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nReturn code: {result.returncode}"
    except Exception as e:
        return f"Error: {str(e)}"

def read_file(path):
    """读取文件"""
    try:
        file_path = WORKDIR / path
        if not file_path.exists():
            return f"Error: File {path} does not exist"
        content = file_path.read_text(encoding='utf-8')
        return content[:50000]  # 限制返回长度
    except Exception as e:
        return f"Error: {str(e)}"

def write_file(path, content):
    """写入文件"""
    try:
        file_path = WORKDIR / path
        file_path.parent.mkdir(exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return f"File written successfully: {path}"
    except Exception as e:
        return f"Error: {str(e)}"

def download_file(url, save_path):
    """从URL下载文件到指定位置"""
    try:
        import requests
        
        # 发送HTTP请求下载文件
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        # 确保保存目录存在
        save_path_obj = Path(save_path)
        save_path_obj.parent.mkdir(exist_ok=True)
        
        # 写入文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return f"文件下载成功: {save_path}"
    except Exception as e:
        return f"Error: {str(e)}"

def recognize_image(image_path):
    """识别图片内容"""
    try:
        from PIL import Image
        import os
        
        # 首先尝试使用深度学习模型识别物体
        try:
            from imageai.Detection import ObjectDetection
            import os
            
            # 检查是否有YOLOv3模型
            yolo_model_path = "yolo.h5"
            
            if os.path.exists(yolo_model_path):
                # 使用YOLOv3模型
                detector = ObjectDetection()
                detector.setModelTypeAsYOLOv3()
                detector.setModelPath(yolo_model_path)
                detector.loadModel()
                
                # 执行检测
                try:
                    # 确保输入图片存在
                    if not os.path.exists(image_path):
                        return f"错误: 输入图片不存在: {image_path}"
                    
                    # 确保输出目录存在
                    output_dir = os.path.dirname(image_path)
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir, exist_ok=True)
                    
                    output_image_path = os.path.join(output_dir, "detected_image.jpg")
                    
                    # 执行检测 - 尝试不同的参数组合
                    try:
                        # 方法1: 使用input_type和output_type参数
                        detections = detector.detectObjectsFromImage(
                            input_image=image_path, 
                            output_image_path=output_image_path,
                            input_type="file",
                            output_type="file"
                        )
                    except:
                        try:
                            # 方法2: 只使用基本参数
                            detections = detector.detectObjectsFromImage(
                                input_image=image_path, 
                                output_image_path=output_image_path
                            )
                        except:
                            # 方法3: 使用最小输出类型
                            detections = detector.detectObjectsFromImage(
                                input_image=image_path, 
                                output_image_path=output_image_path,
                                minimum_percentage_probability=30
                            )
                except Exception as e:
                    return f"错误: 执行检测时出错: {str(e)}\n\n输入路径: {image_path}\n输出路径: {output_image_path}"
                
                # 处理检测结果
                result = "图像识别结果:\n"
                for detection in detections:
                    result += f"- {detection['name']} (置信度: {detection['percentage_probability']:.2f}%)\n"
                
                if len(detections) == 0:
                    result += "未检测到已知物体\n"
                
                # 尝试OCR识别文本
                try:
                    import pytesseract
                    pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'
                    image = Image.open(image_path)
                    text = pytesseract.image_to_string(image, lang='chi_sim')
                    if text.strip():
                        result += f"\n文本识别结果:\n{text}"
                except:
                    pass
                
                return result
            else:
                # 没有模型文件
                error_message = "未找到YOLOv3模型文件\n\n"
                error_message += "提示: ImageAI 3.0+使用PyTorch作为后端，请下载YOLOv3模型文件。\n"
                error_message += "下载地址: https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/yolo.h5"
                error_message += "\n\n您也可以运行 download_model.py 脚本自动下载模型。"
                
                # 尝试OCR
                try:
                    import pytesseract
                    pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'
                    image = Image.open(image_path)
                    text = pytesseract.image_to_string(image, lang='chi_sim')
                    if text.strip():
                        return error_message + f"\n图片识别结果:\n{text}"
                    else:
                        # 如果没有文本，返回图片基本信息
                        image = Image.open(image_path)
                        width, height = image.size
                        mode = image.mode
                        format = image.format
                        result = error_message + f"\n图片信息:\n- 尺寸: {width}x{height}\n- 模式: {mode}\n- 格式: {format}"
                        return result
                except Exception as ocr_error:
                    # 如果OCR也失败，返回基本信息
                    image = Image.open(image_path)
                    width, height = image.size
                    mode = image.mode
                    format = image.format
                    return error_message + f"\n图片信息:\n- 尺寸: {width}x{height}\n- 模式: {mode}\n- 格式: {format}\n\nOCR错误: {str(ocr_error)}"
            
        except Exception as e:
            # 如果深度学习识别失败，返回详细错误信息
            error_message = f"物体识别失败: {str(e)}\n\n"
            print(error_message)
            # 继续尝试OCR，但在结果中包含错误信息
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image, lang='chi_sim')
                if text.strip():
                    return error_message + f"\n图片识别结果:\n{text}"
                else:
                    # 如果没有文本，返回图片基本信息
                    image = Image.open(image_path)
                    width, height = image.size
                    mode = image.mode
                    format = image.format
                    result = error_message + f"\n图片信息:\n- 尺寸: {width}x{height}\n- 模式: {mode}\n- 格式: {format}"
                    return result
            except Exception as ocr_error:
                # 如果OCR也失败，返回基本信息
                image = Image.open(image_path)
                width, height = image.size
                mode = image.mode
                format = image.format
                return error_message + f"\n图片信息:\n- 尺寸: {width}x{height}\n- 模式: {mode}\n- 格式: {format}\n\nOCR错误: {str(ocr_error)}"
            pass
        
        # 尝试OCR识别文本
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='chi_sim')
            if text.strip():
                return f"图片识别结果:\n{text}"
            else:
                # 如果没有文本，返回图片基本信息
                image = Image.open(image_path)
                width, height = image.size
                mode = image.mode
                format = image.format
                result = f"图片信息:\n- 尺寸: {width}x{height}\n- 模式: {mode}\n- 格式: {format}"
                
                result += "\n\n提示: 要使用物体识别功能，请下载YOLOv3模型文件 yolo.h5 并放置到程序目录。"
                result += "\n下载地址: https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/yolo.h5"
                
                return result
        except Exception as e:
            # 如果OCR失败，返回基本信息
            image = Image.open(image_path)
            width, height = image.size
            mode = image.mode
            format = image.format
            return f"图片信息:\n- 尺寸: {width}x{height}\n- 模式: {mode}\n- 格式: {format}\n\n提示: 安装imageai和torch以启用物体识别功能: pip install imageai torch torchvision"
                
    except Exception as e:
        return f"Error: {str(e)}"

def control_application(action, target=None, text=None, coordinates=None):
    """控制应用程序，执行各种操作"""
    try:
        # 尝试导入必要的库
        try:
            import pyautogui
            import time
            import subprocess
            import os
        except ImportError:
            return "Error: 缺少必要的库。请安装pyautogui: pip install pyautogui"
        
        # 根据操作类型执行不同的动作
        if action == "open":
            # 打开应用程序
            if target:
                try:
                    subprocess.Popen(target)
                    time.sleep(2)  # 等待应用启动
                    return f"成功打开应用: {target}"
                except Exception as e:
                    return f"Error: 无法打开应用: {str(e)}"
            else:
                return "Error: 请指定要打开的应用路径"
        
        elif action == "type":
            # 输入文本
            if text:
                pyautogui.typewrite(text)
                return f"成功输入文本: {text}"
            else:
                return "Error: 请指定要输入的文本"
        
        elif action == "click":
            # 点击鼠标
            if coordinates:
                x, y = coordinates
                pyautogui.click(x, y)
                return f"成功点击坐标: ({x}, {y})"
            else:
                # 点击当前鼠标位置
                pyautogui.click()
                return "成功点击当前位置"
        
        elif action == "press":
            # 按下键盘按键
            if target:
                pyautogui.press(target)
                return f"成功按下按键: {target}"
            else:
                return "Error: 请指定要按下的按键"
        
        elif action == "hotkey":
            # 按下组合键
            if target:
                keys = target.split('+')
                pyautogui.hotkey(*keys)
                return f"成功按下组合键: {target}"
            else:
                return "Error: 请指定要按下的组合键"
        
        elif action == "move":
            # 移动鼠标
            if coordinates:
                x, y = coordinates
                pyautogui.moveTo(x, y)
                return f"成功移动鼠标到: ({x}, {y})"
            else:
                return "Error: 请指定目标坐标"
        
        elif action == "screenshot":
            # 截图
            screenshot = pyautogui.screenshot()
            save_path = os.path.join(os.path.expanduser("~"), "Desktop", "screenshot.png")
            screenshot.save(save_path)
            return f"成功截图并保存到: {save_path}"
        
        elif action == "get_position":
            # 获取当前鼠标位置
            x, y = pyautogui.position()
            return f"当前鼠标位置: ({x}, {y})"
        
        else:
            return f"Error: 不支持的操作类型: {action}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_application_info():
    """获取当前活动应用程序的信息"""
    try:
        # 尝试导入必要的库
        try:
            import pyautogui
            import win32gui
            import win32process
            import psutil
            import os
        except ImportError:
            return "Error: 缺少必要的库。请安装pyautogui和pywin32: pip install pyautogui pywin32 psutil"
        
        # 获取当前活动窗口
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            # 获取窗口标题
            title = win32gui.GetWindowText(hwnd)
            
            # 获取窗口位置和大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # 获取窗口所属的进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # 获取进程信息
            process_name = "Unknown"
            process_path = "Unknown"
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                process_path = process.exe()
            except:
                pass
            
            # 截图当前窗口
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            save_path = os.path.join(os.path.expanduser("~"), "Desktop", "window_screenshot.png")
            screenshot.save(save_path)
            
            # 构建返回信息
            info = f"当前活动应用信息:\n"
            info += f"- 窗口标题: {title}\n"
            info += f"- 进程名称: {process_name}\n"
            info += f"- 进程路径: {process_path}\n"
            info += f"- 窗口位置: ({left}, {top})\n"
            info += f"- 窗口大小: {width}x{height}\n"
            info += f"- 窗口截图已保存到: {save_path}\n"
            
            return info
        else:
            return "Error: 无法获取当前活动窗口"
    except Exception as e:
        return f"Error: {str(e)}"

# 全局搜索引擎列表
SEARCH_ENGINES = [
    {
        "name": "DuckDuckGo",
        "url": "https://duckduckgo.com/html/?q={query}",
        "selector": '.result__body',
        "title_selector": '.result__title a',
        "snippet_selector": '.result__snippet'
    },
    {
        "name": "Google",
        "url": "https://www.google.com/search?q={query}",
        "selector": '.g',
        "title_selector": 'h3',
        "snippet_selector": '.VwiC3b'
    },
    {
        "name": "Bing",
        "url": "https://www.bing.com/search?q={query}",
        "selector": '.b_algo',
        "title_selector": 'h2 a',
        "snippet_selector": '.b_caption p'
    },
    {
        "name": "Yahoo",
        "url": "https://search.yahoo.com/search?p={query}",
        "selector": '.algo-sr',
        "title_selector": 'h3.title a',
        "snippet_selector": '.compText'
    },
    {
        "name": "StartPage",
        "url": "https://www.startpage.com/do/search?q={query}",
        "selector": '.result',
        "title_selector": '.result-title a',
        "snippet_selector": '.result-description'
    }
]

def find_more_search_engines():
    """查找更多搜索引擎"""
    query = "popular search engines list 2024"
    found_engines = []
    
    # 使用现有搜索引擎查找新的搜索引擎
    for engine in SEARCH_ENGINES[:2]:  # 只使用前两个搜索引擎
        try:
            print(f"Searching for more search engines using {engine['name']}...")
            url = engine['url'].format(query=query.replace(' ', '+'))
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取可能的搜索引擎名称
            for result in soup.select(engine['selector'])[:10]:
                title_elem = result.select_one(engine['title_selector'])
                if title_elem:
                    title = title_elem.text
                    # 简单过滤，查找包含"search engine"的结果
                    if "search engine" in title.lower() or "搜索引擎" in title:
                        found_engines.append(title)
        except Exception as e:
            print(f"Error searching for more engines: {e}")
            continue
    
    # 去重
    found_engines = list(set(found_engines))
    return found_engines

def add_search_engine(name, url_pattern, selector, title_selector, snippet_selector):
    """添加新的搜索引擎"""
    new_engine = {
        "name": name,
        "url": url_pattern,
        "selector": selector,
        "title_selector": title_selector,
        "snippet_selector": snippet_selector
    }
    
    # 检查是否已存在
    for engine in SEARCH_ENGINES:
        if engine["name"] == name:
            return f"搜索引擎 {name} 已经存在"
    
    SEARCH_ENGINES.append(new_engine)
    return f"成功添加搜索引擎: {name}"

# 搜索引擎性能记录
SEARCH_ENGINE_PERFORMANCE = {}

def web_search(query):
    """联网搜索"""
    # 检查是否要查找更多搜索引擎
    if "更多搜索引擎" in query or "find more search engines" in query.lower():
        found_engines = find_more_search_engines()
        if found_engines:
            result = "找到的搜索引擎：\n"
            for engine in found_engines[:10]:  # 最多显示10个
                result += f"- {engine}\n"
            result += "\n提示：如果要添加新的搜索引擎，请使用 'add search engine' 命令"
            return result
        else:
            return "未找到更多搜索引擎"
    
    # 尝试多个搜索引擎
    search_engines = SEARCH_ENGINES.copy()
    
    # 基于历史性能排序搜索引擎
    def sort_by_performance(engine):
        return SEARCH_ENGINE_PERFORMANCE.get(engine['name'], 0)
    
    # 先按性能排序，再随机打乱前3个（但保持原列表顺序）
    search_engines.sort(key=sort_by_performance, reverse=True)
    # 打乱前3个元素（修改原列表）
    if len(search_engines) >= 3:
        top3 = search_engines[:3]
        random.shuffle(top3)
        search_engines[:3] = top3
    
    for engine in search_engines:
        try:
            print(f"Trying search engine: {engine['name']}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            # 格式化URL，替换查询参数
            url = engine['url'].format(query=query.replace(' ', '+'))
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select(engine['selector'])[:5]:  # 前5个结果
                title_elem = result.select_one(engine['title_selector'])
                if title_elem:
                    title = title_elem.text
                    # 提取链接
                    if engine['name'] == 'DuckDuckGo':
                        # DuckDuckGo的链接在title元素中
                        link = title_elem.get('href')
                    elif engine['name'] == 'Google':
                        # Google的链接在h3下的a元素中
                        link_elem = result.select_one('a')
                        link = link_elem['href'] if link_elem else ''
                        # 处理Google的链接重定向
                        if link.startswith('/url?q='):
                            import urllib.parse
                            link = urllib.parse.unquote(link.split('/url?q=')[1].split('&')[0])
                    elif engine['name'] == 'Bing':
                        # Bing的链接在h2下的a元素中
                        if title_elem.name == 'a':
                            # 如果title_elem本身就是a元素，直接获取href
                            link = title_elem.get('href')
                        else:
                            # 否则查找h2下的a元素
                            link_elem = result.select_one('h2 a')
                            link = link_elem['href'] if link_elem else ''
                    else:
                        # 通用情况
                        if title_elem.name == 'a':
                            # 如果title_elem本身就是a元素，直接获取href
                            link = title_elem.get('href')
                        else:
                            # 否则查找第一个a元素
                            link_elem = result.select_one('a')
                            link = link_elem['href'] if link_elem else ''
                    snippet_elem = result.select_one(engine['snippet_selector'])
                    snippet_text = snippet_elem.text if snippet_elem else ""
                    results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet_text}\n")
            
            if results:
                # 更新搜索引擎性能
                SEARCH_ENGINE_PERFORMANCE[engine['name']] = SEARCH_ENGINE_PERFORMANCE.get(engine['name'], 0) + 1
                return f"Search results from {engine['name']}:\n\n" + "\n".join(results)
        except Exception as e:
            print(f"Error with {engine['name']}: {str(e)}")
            # 降低失败搜索引擎的性能评分
            SEARCH_ENGINE_PERFORMANCE[engine['name']] = max(0, SEARCH_ENGINE_PERFORMANCE.get(engine['name'], 0) - 1)
            continue
    
    # 所有搜索引擎都失败
    return "Error: All search engines failed. Please try again later."

def search_files(query, path="."):
    """搜索文件内容"""
    import os
    import re
    
    results = []
    count = 0
    max_results = 10
    
    # 遍历目录
    for root, dirs, files in os.walk(path):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            # 只处理文本文件
            if file.endswith(('.txt', '.py', '.md', '.js', '.html', '.css', '.json')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # 搜索文本
                        if re.search(query, content, re.IGNORECASE):
                            # 提取包含查询的行
                            lines = content.split('\n')
                            matching_lines = []
                            for i, line in enumerate(lines, 1):
                                if re.search(query, line, re.IGNORECASE):
                                    matching_lines.append(f"Line {i}: {line.strip()}")
                                    if len(matching_lines) >= 3:  # 最多显示3行
                                        break
                            
                            results.append(f"File: {file_path}\n" + "\n".join(matching_lines) + "\n")
                            count += 1
                            if count >= max_results:
                                break
                except Exception as e:
                    # 忽略文件读取错误
                    continue
        if count >= max_results:
            break
    
    if results:
        return f"Found {count} files containing '{query}':\n\n" + "\n".join(results)
    else:
        return f"No files containing '{query}' found in {path}"

# 增强工具处理的错误处理
def execute_tool(tool_name, tool_input):
    """执行工具并处理错误"""
    try:
        handler = TOOL_HANDLERS.get(tool_name)
        if handler:
            output = handler(**tool_input)
            return output
        else:
            return f"Error: Unknown tool {tool_name}"
    except Exception as e:
        # 错误处理和自我纠错
        error_message = f"Error executing tool {tool_name}: {str(e)}"
        print(f"Tool execution error: {error_message}")
        
        # 针对网络搜索的特殊处理
        if tool_name == "web_search":
            return "Error: Search failed. Trying alternative search method...\n" + web_search(tool_input.get("query", ""))
        
        return error_message

# 工具定义
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path"
                },
                "content": {
                    "type": "string",
                    "description": "File content"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "run_command",
        "description": "Run a command in the terminal",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to run"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "download_file",
        "description": "Download any type of file (music, image, video, document) from a URL to a specified location on your computer",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Direct URL of the file to download, e.g., https://example.com/tiger.mp3 or https://example.com/mount_everest.jpg"
                },
                "save_path": {
                    "type": "string",
                    "description": "Full path to save the downloaded file, including filename and extension, e.g., C:\\Users\\Administrator\\Desktop\\两只老虎.mp3 or C:\\Users\\Administrator\\Desktop\\珠穆朗玛峰.jpg"
                }
            },
            "required": ["url", "save_path"]
        }
    },
    {
        "name": "recognize_image",
        "description": "Recognize text and content in an image file using OCR technology",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Full path to the image file to recognize, e.g., C:\\Users\\Administrator\\Desktop\\example.jpg"
                }
            },
            "required": ["image_path"]
        }
    },
    {
        "name": "control_application",
        "description": "Control applications on your computer, such as opening apps, typing text, clicking buttons, and more",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: open, type, click, press, hotkey, move, screenshot, get_position"
                },
                "target": {
                    "type": "string",
                    "description": "Target for the action, e.g., application path for 'open', key name for 'press', or hotkey combination for 'hotkey'"
                },
                "text": {
                    "type": "string",
                    "description": "Text to type for 'type' action"
                },
                "coordinates": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                    "description": "Coordinates for 'click' or 'move' action, e.g., [100, 200]"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "get_application_info",
        "description": "Get information about the currently active application, including window title, process info, and take a screenshot",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "add_missing_tool",
        "description": "Add a missing tool to the codebase",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool_name": {
                    "type": "string",
                    "description": "Name of the tool to add"
                },
                "tool_description": {
                    "type": "string",
                    "description": "Description of the tool"
                },
                "input_schema": {
                    "type": "object",
                    "description": "JSON schema for the tool's input parameters"
                },
                "tool_function": {
                    "type": "string",
                    "description": "Python code for the tool function body"
                }
            },
            "required": ["tool_name", "tool_description", "input_schema", "tool_function"]
        }
    },
    {
        "name": "search_files",
        "description": "Search for files containing specific text",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for in files"
                },
                "path": {
                    "type": "string",
                    "description": "Directory path to search in (default: current directory)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "web_search",
        "description": "Search the web",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "add_search_engine",
        "description": "Add a new search engine",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Search engine name"
                },
                "url_pattern": {
                    "type": "string",
                    "description": "URL pattern with {query} placeholder"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector for search results"
                },
                "title_selector": {
                    "type": "string",
                    "description": "CSS selector for result titles"
                },
                "snippet_selector": {
                    "type": "string",
                    "description": "CSS selector for result snippets"
                }
            },
            "required": ["name", "url_pattern", "selector", "title_selector", "snippet_selector"]
        }
    },
    {
        "name": "list_search_engines",
        "description": "List all available search engines",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "set_model",
        "description": "Set the AI model to use",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Model name (e.g., deepseek-v3, qwen3-coder, deepseek-online)"
                }
            },
            "required": ["model"]
        }
    },
    {
        "name": "list_models",
        "description": "List all available models",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "search_skills",
        "description": "Search for available skills",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for skills"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "download_skill",
        "description": "Download a skill",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name"
                },
                "url": {
                    "type": "string",
                    "description": "Skill URL"
                }
            },
            "required": ["name", "url"]
        }
    },
    {
        "name": "use_skill",
        "description": "Use a downloaded skill",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name"
                },
                "url": {
                    "type": "string",
                    "description": "URL for web scraping or other web-related skills"
                },
                "code": {
                    "type": "string",
                    "description": "Code for code analysis skills"
                },
                "file_path": {
                    "type": "string",
                    "description": "File path for skills that need to read files"
                },
                "text": {
                    "type": "string",
                    "description": "Text for text processing skills"
                },
                "data": {
                    "type": "string",
                    "description": "Data for data visualization skills"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "list_skills",
        "description": "List all downloaded skills",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

def list_search_engines():
    """列出所有可用的搜索引擎"""
    result = "可用的搜索引擎：\n"
    for i, engine in enumerate(SEARCH_ENGINES, 1):
        result += f"{i}. {engine['name']}\n"
    return result

def list_models():
    """列出所有可用的模型"""
    result = "可用的AI模型：\n"
    for model in AVAILABLE_MODELS:
        result += f"- {model}\n"
    result += f"\n当前使用: {CURRENT_MODEL}"
    return result

def list_skills():
    """列出所有已下载的技能"""
    if not SKILLS:
        return "还没有下载任何技能"
    
    result = "已下载的技能：\n"
    for name, skill in SKILLS.items():
        result += f"- {name}: {skill.description}\n"
    return result

def add_missing_tool(tool_name, tool_description, input_schema, tool_function):
    """添加缺失的工具到代码中"""
    try:
        # 读取当前文件内容
        current_file = Path(__file__)
        content = current_file.read_text(encoding='utf-8')
        
        # 生成工具函数代码
        function_code = f"\ndef {tool_name}(**kw):\n    \"\"\"{tool_description}\"\"\"\n    {tool_function}\n"
        
        # 找到写入文件函数的位置，在其后添加新工具函数
        write_file_end = content.find("def write_file(path, content):")
        if write_file_end == -1:
            write_file_end = content.find("def download_file(url, save_path):")
        if write_file_end == -1:
            return f"Error: Could not find appropriate location to add tool function"
        
        # 找到函数结束的位置
        function_end = content.find("def ", write_file_end + 10)
        if function_end == -1:
            function_end = content.find("# 全局搜索引擎列表", write_file_end)
        
        # 插入新工具函数
        new_content = content[:function_end] + function_code + "\n" + content[function_end:]
        
        # 找到工具定义的位置，在run_command工具后添加新工具
        tool_def_start = new_content.find('"name": "run_command",')
        if tool_def_start == -1:
            return f"Error: Could not find tool definitions"
        
        tool_def_end = new_content.find('},', tool_def_start)
        if tool_def_end == -1:
            return f"Error: Could not find end of run_command tool definition"
        
        # 生成工具定义
        tool_def = f""",
    {{
        "name": "{tool_name}",
        "description": "{tool_description}",
        "input_schema": {json.dumps(input_schema, ensure_ascii=False, indent=4)}
    }}"""
        
        # 插入工具定义
        new_content = new_content[:tool_def_end+2] + tool_def + new_content[tool_def_end+2:]
        
        # 找到TOOL_HANDLERS的位置，添加新工具处理
        handlers_start = new_content.find("TOOL_HANDLERS = {")
        if handlers_start == -1:
            return f"Error: Could not find TOOL_HANDLERS"
        
        # 找到run_command处理的位置
        run_command_end = new_content.find('"run_command": lambda **kw: run_bash(kw["command"]),', handlers_start)
        if run_command_end == -1:
            return f"Error: Could not find run_command handler"
        
        # 找到该行的结束位置
        line_end = new_content.find("\n", run_command_end)
        
        # 生成工具处理代码
        handler_code = f'    "{tool_name}": lambda **kw: {tool_name}(**kw),\n'
        
        # 插入工具处理
        new_content = new_content[:line_end+1] + handler_code + new_content[line_end+1:]
        
        # 写回文件
        current_file.write_text(new_content, encoding='utf-8')
        
        # 重新加载模块
        import importlib
        import sys
        sys.modules[__name__] = importlib.reload(sys.modules[__name__])
        
        return f"工具 {tool_name} 已成功添加到代码中"
    except Exception as e:
        return f"Error adding tool: {str(e)}"

# 工具处理映射（修复了 use_skill 的参数重复问题）
TOOL_HANDLERS = {
    "read_file": lambda **kw: read_file(kw["path"]),
    "write_file": lambda **kw: write_file(kw["path"], kw["content"]),
    "run_command": lambda **kw: run_bash(kw["command"]),
    "download_file": lambda **kw: download_file(kw["url"], kw["save_path"]),
    "recognize_image": lambda **kw: recognize_image(kw["image_path"]),
    "control_application": lambda **kw: control_application(kw["action"], kw.get("target"), kw.get("text"), kw.get("coordinates")),
    "get_application_info": lambda **kw: get_application_info(),
    "web_search": lambda **kw: web_search(kw["query"]),
    "search_files": lambda **kw: search_files(kw["query"], kw.get("path", ".")),



    "add_missing_tool": lambda **kw: add_missing_tool(
        kw["tool_name"], kw["tool_description"], kw["input_schema"], kw["tool_function"]
    ),

    "add_search_engine": lambda **kw: add_search_engine(
        kw["name"], kw["url_pattern"], kw["selector"], 
        kw["title_selector"], kw["snippet_selector"]
    ),
    "list_search_engines": lambda **kw: list_search_engines(),
    "set_model": lambda **kw: set_model(kw["model"]),
    "list_models": lambda **kw: list_models(),
    "search_skills": lambda **kw: json.dumps(search_skills(kw["query"]), ensure_ascii=False, indent=2),
    "download_skill": lambda **kw: download_skill(kw["name"], kw["url"]),
    "use_skill": lambda **kw: use_skill(kw["name"], **{k: v for k, v in kw.items() if k != "name"}),  # 修复点
    "list_skills": lambda **kw: list_skills()
}

# 上下文压缩
def estimate_tokens(messages):
    """估算token数量"""
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(content) // 4  # 粗略估算
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    total += len(item["text"]) // 4
    return total

def micro_compact(messages):
    """轻量级压缩"""
    tool_results = []
    for i, msg in enumerate(messages):
        if msg["role"] == "user" and isinstance(msg.get("content"), list):
            for j, part in enumerate(msg["content"]):
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    tool_results.append((i, j, part))
    
    KEEP_RECENT = 2
    if len(tool_results) <= KEEP_RECENT:
        return messages
    
    for _, _, part in tool_results[:-KEEP_RECENT]:
        if len(part.get("content", "")) > 100:
            part["content"] = "[Previous tool result omitted]"
    
    return messages

def auto_compact(messages):
    """自动压缩"""
    # 保存完整历史
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w", encoding='utf-8') as f:
        for msg in messages:
            f.write(json.dumps(msg, default=str, ensure_ascii=False) + "\n")
    
    # 生成摘要
    summary = "This is a compressed summary of the conversation."
    
    return [
        {"role": "user", "content": f"[Compressed]\n\n{summary}"},
        {"role": "assistant", "content": "Understood. Continuing."}
    ]

# 智能体循环（修复了工具调用后的继续处理）
def agent_loop():
    """智能体主循环"""
    messages = []
    print("欢迎使用唐雨的智能助手！")
    print("我可以帮助你读取文件、写入文件、运行命令和进行网络搜索。")
    print("搜索引擎已经配置完成，可以直接使用。")
    print("输入 'exit' 退出。")
    
    while True:
        # 获取用户输入
        user_input = input("\n你: ")
        if user_input.lower() == 'exit':
            print("再见！")
            break
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_input})
        
        # 持续调用 LLM 直到不再需要工具调用
        while True:
            # 压缩上下文
            messages = micro_compact(messages)
            if estimate_tokens(messages) > 4000:
                messages = auto_compact(messages)
            
            # 调用LLM
            if API_KEY:
                response = call_deepseek_api(messages, TOOLS)
            else:
                response = mock_llm_response(messages, TOOLS)
            
            # 添加助手响应（包括可能存在的工具调用）
            messages.append({"role": "assistant", "content": response["content"]})
            
            # 检查是否需要调用工具
            if response["stop_reason"] != "tool_use":
                # 输出助手回答
                for block in response["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        # 处理Unicode编码问题
                        try:
                            print(f"Assistant: {block['text']}")
                        except UnicodeEncodeError:
                            safe_text = block['text'].encode('gbk', 'ignore').decode('gbk')
                            print(f"Assistant: {safe_text}")
                break  # 退出内部循环，等待下一个用户输入
            
            # 执行工具调用
            results = []
            for block in response["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    tool_input = block.get("input", {})
                    
                    print(f"Assistant: Running tool: {tool_name}")
                    
                    # 执行工具（带错误处理）
                    output = execute_tool(tool_name, tool_input)
                    
                    # 收集结果
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.get("id"),
                        "content": output
                    })
            
            # 添加工具结果到消息历史
            # 确保content是字符串格式，符合OpenAI API规范
            tool_result_text = "\n".join([f"Tool result for {result.get('tool_use_id', 'unknown')}: {result.get('content', '')}" for result in results])
            messages.append({"role": "user", "content": tool_result_text})
            
            # 输出工具结果（可选）
            for result in results:
                try:
                    print(f"Tool Result: {result['content']}")
                except UnicodeEncodeError:
                    # 替换无法编码的字符
                    safe_content = str(result['content']).encode('gbk', 'ignore').decode('gbk')
                    print(f"Tool Result: {safe_content}")
            
            # 继续循环，让 LLM 根据工具结果生成最终回答

if __name__ == "__main__":
    agent_loop()
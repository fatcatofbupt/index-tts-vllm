import requests
import time
import os
from pathlib import Path
import pyrootutils
ROOT = pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
def tts_client():
    # 配置
    base_url = "http://localhost:11996"  # 根据实际服务地址修改
    speaker = "jay_klee"  # 根据实际可用角色名修改
    speaker = "67a0410a81974dbb94a51c211aee2499"  # 根据实际可用角色名修改
    input_file = "lines.txt"
    output_dir = "tts_output"
    
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 读取文本行
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # 处理每一行文本
    for i, text in enumerate(lines):
        print(f"Processing line {i+1}/{len(lines)}: {text}")
        
        # 准备请求数据
        payload = {
            "text": text,
            "character": speaker
        }
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 发送TTS请求
            response = requests.post(f"{base_url}/tts_url", json=payload)
            # response = requests.post(f"{base_url}/tts", json=payload)
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                # 生成文件名（使用部分文本内容+时间延迟）
                # 清理文件名中的非法字符
                safe_text = "".join(c for c in text[:20] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{speaker}_{safe_text}_{elapsed_time:.2f}s.wav"
                filepath = os.path.join(output_dir, filename)
                
                # 保存音频文件
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                print(f"  Saved: {filename} (took {elapsed_time:.2f}s)")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  Exception occurred: {str(e)}")
        
        # 可选：添加短暂延迟避免请求过于频繁
        time.sleep(0.1)

if __name__ == "__main__":
    tts_client()
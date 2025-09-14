# generate_speaker_json.py
import json
from pathlib import Path
import pyrootutils
ROOT = pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
def generate_speaker_json(assets_dir: str = "assets", output_file: str = "speaker.json"):
    """
    扫描 assets 目录下的音频文件，生成 speaker.json
    
    Args:
        assets_dir: 音频文件根目录
        output_file: 输出的 JSON 文件路径
    """
    # 创建 Path 对象
    assets_path = ROOT / assets_dir
    output_file = assets_path / output_file
    
    # 检查目录是否存在
    if not assets_path.exists():
        raise FileNotFoundError(f"目录 {assets_dir} 不存在")
    
    # 存储 speaker 信息的字典
    speakers = {}
    
    # 遍历所有子目录和文件
    for speaker_dir in assets_path.iterdir():
        if speaker_dir.is_dir():
            # 获取该目录下的所有音频文件
            audio_files = list(speaker_dir.glob("*.wav")) + list(speaker_dir.glob("*.mp3"))
            
            # 如果子目录内还有子目录（如 wangrui/0.wav 的情况）
            for sub_dir in speaker_dir.rglob("*"):
                if sub_dir.is_file() and sub_dir.suffix in [".wav", ".mp3"]:
                    audio_files.append(sub_dir)
            
            # 将相对路径转换为字符串并添加到 speakers 字典
            if audio_files:
                speakers[speaker_dir.name] = [str(f.relative_to(assets_path.parent)) 
                                             for f in audio_files]
    
    # 写入 JSON 文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(speakers, f, ensure_ascii=False, indent=4)
    
    print(f"已生成 {output_file}，包含 {len(speakers)} 位 speaker")

# 使用示例
if __name__ == "__main__":
    generate_speaker_json()
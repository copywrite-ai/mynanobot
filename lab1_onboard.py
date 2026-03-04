import os
import json
from pathlib import Path

def onboard():
    """让你的 AI 助手‘入住’你的电脑"""
    
    # 1. 定义配置文件的藏身之处 (用户家目录下的 .mybot 文件夹)
    config_dir = Path.home() / ".mybot"
    config_file = config_dir / "config.json"

    print("🚀 正在为你初始化 AI 助手环境...")

    # 2. 如果文件夹不存在，就建一个
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
        print(f"✅ 已创建配置文件夹: {config_dir}")

    # 3. 准备一份默认的“个人名片”(配置文件)
    default_config = {
        "api_key": "在这里输入你的 API Key",
        "model": "gpt-4o",
        "temperature": 0.7
    }

    # 4. 如果文件还没建立，就写进去
    if not config_file.exists():
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        print(f"✅ 已生成默认配置文件: {config_file}")
    else:
        print(f"⚠️ 配置文件已存在，跳过生成。")

    print("\n🎉 初始化完成！")
    print(f"👉 请打开 {config_file} 并填入你的 API Key 就可以开始下一步啦！")

if __name__ == "__main__":
    onboard()

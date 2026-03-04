import typer
import json
from pathlib import Path
from rich.console import Console

# 1. 初始化 Typer 应用 (就像 nanobot/cli/commands.py 第 24 行那样)
app = typer.Typer()
console = Console()

@app.command()
def onboard():
    """初始化你的 AI 助手环境"""
    config_dir = Path.home() / ".mybot"
    config_file = config_dir / "config.json"

    console.print("[bold blue]🚀 正在为你初始化 AI 助手环境...[/bold blue]")

    if not config_dir.exists():
        config_dir.mkdir(parents=True)
        console.print(f"[green]✅ 已创建配置文件夹: {config_dir}[/green]")

    default_config = {
        "api_key": "在这里输入你的 API Key",
        "model": "gpt-4o"
    }

    if not config_file.exists():
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        console.print(f"[green]✅ 已生成默认配置文件: {config_file}[/green]")
    else:
        # 使用 Typer 的确认对话框
        if typer.confirm("配置文件已存在，是否要重置为默认值？"):
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            console.print("[yellow]已重置配置文件。[/yellow]")

@app.command()
def info():
    """查看助手的基本信息"""
    console.print("[bold]MyBot v0.1.0[/bold]")
    console.print("这是你的第一个 AI 智能体工程！")

if __name__ == "__main__":
    # 启动 Typer
    app()

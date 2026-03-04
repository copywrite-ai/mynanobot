import re
from pathlib import Path

class NanobotSecurityMirror:
    """
    镜像 nanobot/agent/tools/shell.py 中的安全防御逻辑。
    用于在不破坏系统的前提下，进行绕过测试。
    """
    def __init__(self):
        # 复制自 nanobot 源码的黑名单
        self.deny_patterns = [
            r"\brm\s+-[rf]{1,2}\b",          # rm -r, rm -rf, rm -fr
            r"\bdel\s+/[fq]\b",              # del /f, del /q
            r"\brmdir\s+/s\b",               # rmdir /s
            r"(?:^|[;&|]\s*)format\b",       # format
            r"\b(mkfs|diskpart)\b",          # disk operations
            r"\bdd\s+if=",                   # dd
            r">\s*/dev/sd",                  # write to disk
            r"\b(shutdown|reboot|poweroff)\b",  # system power
            r":\(\)\s*\{.*\};\s*:",          # fork bomb
        ]

    def check_command(self, command: str) -> bool:
        """返回 True 表示安全，False 表示被拦截"""
        cmd = command.strip().lower()
        for pattern in self.deny_patterns:
            if re.search(pattern, cmd):
                print(f"❌ 拦截成功！匹配到危险模式: {pattern}")
                return False
        return True

def run_test_suite():
    mirror = NanobotSecurityMirror()
    
    test_cases = [
        ("ls -la", "正常命令"),
        ("rm -rf /", "直接攻击 (黑名单目标)"),
        ("echo 'cm0gLXJmIC8=' | base64 -d | bash", "Base64 混淆绕过"),
        ("printf '\\x72\\x6d\\x20\\x2d\\x72\\x66\\x20\\x2f' | bash", "Hex 混淆绕过"),
        ("python3 -c 'import os; os.system(\"rm -rf /\")'", "代码注入扩展绕过"),
        ("rm\t-rf\t/", "空白字符混淆"),
    ]

    print("=== nanobot 安全防御能力压力测试 ===\n")
    for cmd, desc in test_cases:
        print(f"测试点: {desc}")
        print(f"输入命令: {cmd}")
        is_safe = mirror.check_command(cmd)
        if is_safe:
            print("⚠️ 警告：命令绕过了正则拦截！系统可能面临风险。")
        print("-" * 40)

if __name__ == "__main__":
    run_test_suite()

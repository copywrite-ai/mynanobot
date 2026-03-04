#!/bin/bash
# 内存监控脚本 - 每个整点汇报内存使用情况

# 获取当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 生成内存报告
MEMORY_INFO=$(free -h)

# 输出格式化报告
echo "========================================"
echo "📊 内存使用报告"
echo "⏰ 时间：$TIMESTAMP"
echo "========================================"
# 格式化输出内存信息
TOTAL_MEM=$(free -h | grep Mem | awk '{print $2}')
USED_MEM=$(free -h | grep Mem | awk '{print $3}')
FREE_MEM=$(free -h | grep Mem | awk '{print $4}')
AVAIL_MEM=$(free -h | grep Mem | awk '{print $7}')

echo "总内存：$TOTAL_MEM"
echo "已使用：$USED_MEM"
echo "空闲：$FREE_MEM"
echo "可用：$AVAIL_MEM"
echo "========================================"

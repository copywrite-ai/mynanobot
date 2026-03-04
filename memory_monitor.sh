#!/bin/bash

# 内存监控脚本 - 每 5 分钟执行一次
echo "=== $(date) ===" >> /var/log/memory_check.log
free -h
echo "" >> /var/log/memory_check.log

# 显示当前内存状态
echo "当前内存使用情况:"
free -h | grep Mem
echo "---"

#!/bin/bash

# 检查系统内存使用情况
echo "=== $(date) ===" >> /var/log/memory_check.log
free -h
echo "" >> /var/log/memory_check.log

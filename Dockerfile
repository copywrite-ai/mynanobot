# Use a mirrored base image for acceleration
FROM docker.1ms.run/python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (using debian mirror if needed, but keeping it simple for now)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
# Use a domestic pip mirror for faster installation
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    lark-oapi \
    openai \
    pydantic \
    pydantic-settings \
    requests \
    loguru \
    croniter \
    urllib3==1.26.18 \
    chardet==4.0.0

# Copy the current directory contents into the container at /app
COPY . /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "lab8_framework_bot.py"]

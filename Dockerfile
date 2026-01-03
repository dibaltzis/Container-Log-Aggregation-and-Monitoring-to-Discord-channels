# Use lightweight Python base image for ARM & AMD64
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy source code
COPY src/ /app/src/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "src/main.py"]

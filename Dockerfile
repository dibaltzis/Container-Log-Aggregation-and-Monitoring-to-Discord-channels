# Use lightweight Python base image for ARM & AMD64
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Build version argument and label
ARG VERSION
LABEL build.version="${VERSION}"
ENV APP_VERSION="${VERSION}"

# Copy requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ /app/src/

ENV PYTHONUNBUFFERED=1
# Run the bot
CMD ["python", "src/main.py"]

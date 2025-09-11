# Use a slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY reqs.txt .
RUN pip install -r reqs.txt

# Copy your source code
COPY . .

# Run your bot
CMD ["python", "SnipeBot.py"]

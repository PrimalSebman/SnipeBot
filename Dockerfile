# Use a slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY reqs.txt .
RUN pip install -r reqs.txt

# Copy your source code
COPY . .

# Copy the Firebase key into the container
COPY firebase-key.json /app/firebase-key.json

# Environment variables (DISCORD_TOKEN will be set in Cloud Run console)
ENV FIREBASE_KEY=/app/firebase-key.json

# Run your bot
CMD ["python", "SnipeBot.py"]

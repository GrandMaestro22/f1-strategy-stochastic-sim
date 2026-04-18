# 1. Use a lightweight Python 'Base Image'
FROM python:3.12-slim

# 2. Set the 'Home' folder inside the container
WORKDIR /app

# 3. Copy your project files into the container
COPY . .

# 4. Command to run your simulator automatically
CMD ["python", "main.py"]
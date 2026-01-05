# 1. Lightweight version of Python 3.11
FROM python:3.11-slim

# 2. Working directory inside the container
WORKDIR /app

# 3. Copy dependencies first
COPY app/requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY app/ .

# 6. Expose port 8000 so Kubernetes can reach the app
EXPOSE 8000

# 7. Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
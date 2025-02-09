FROM python:3.9-slim

# working directory
WORKDIR /app

# Copy to /app
COPY . /app


RUN pip install --no-cache-dir -r requirements.txt

# FastAPI port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

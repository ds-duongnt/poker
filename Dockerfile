# Start with python 3.10 image
FROM python:3.10-slim

# Copy the current directory into /app on the image
WORKDIR /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Entry point command
CMD ["python", "main.py"]
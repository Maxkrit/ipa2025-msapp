FROM python:3.9-slim

WORKDIR /app

# Install all dependencies with specific, compatible versions
RUN pip install --no-cache-dir flask==2.2.2 pymongo==4.3.3 Jinja2==3.1.2 MarkupSafe==2.1.1 werkzeug==2.2.2

# Copy the application code into the image
COPY . .

# Command to run the application
CMD ["python", "app.py"]
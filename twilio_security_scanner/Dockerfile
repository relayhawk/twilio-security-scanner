FROM python:3.12-slim

WORKDIR /app

# Create package directory
RUN mkdir -p /app/twilio_security_scanner

# Copy requirements first to leverage Docker's layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python files into the package directory
COPY . /app/twilio_security_scanner/

# Set Python path to recognize the module
ENV PYTHONPATH=/app

CMD ["python", "-m", "twilio_security_scanner.cli"]
# Getting image from dockerhub
FROM python:3.8.0-buster

# Make a workdirectory to put in all code files
WORKDIR /app

#Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy our source code
copy /app .

# Run the application
CMD ["python", "index.py"]
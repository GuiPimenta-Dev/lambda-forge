# Start with a Python base image
FROM python:3.9-slim

# Install Node.js
RUN apt-get update && \
  apt-get install -y nodejs npm && \
  rm -rf /var/lib/apt/lists/*

# Confirm installations
RUN node --version
RUN npm --version
RUN python --version
RUN pip --version


RUN pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/

# Install Python packages from both PyPI and Test PyPI
RUN pip install aws-cdk-lib

# Set the working directory in the container
WORKDIR /app

# Install AWS CDK globally
RUN npm install -g aws-cdk


# Copy the local code to the container
COPY . .

# Run CDK synth as the final step
CMD ["cdk", "synth"]

FROM python:3.9-slim

WORKDIR /lambda-forge

COPY . /lambda-forge

# Install necessary dependencies
RUN apt-get update \
  && apt-get install -y curl jq gnupg graphviz \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install nvm and Node.js
ENV NODE_VERSION=16.13.0
ENV NVM_DIR=/root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash \
  && . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION} \
  && . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION} \
  && . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}

# Ensure Node.js and npm are correctly installed
ENV PATH="$NVM_DIR/versions/node/v${NODE_VERSION}/bin:$PATH"
RUN node --version
RUN npm --version

# Install Node.js global dependencies
RUN npm install -g aws-cdk redoc-cli cdk-assets@2

# Install Python dependencies
RUN pip install --upgrade pip \
  && pip install pyyaml pytest-html coverage awscli boto3==1.33.2 botocore==1.33.2 \
  && pip install -r base-requirements.txt \
  && pip install lambda-forge

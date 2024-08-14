FROM python:3.9-slim

WORKDIR /lambda-forge

COPY . /lambda-forge

# Install nvm with Node.js and npm
ENV NODE_VERSION=16.13.0
RUN apt-get update \
  && apt-get install -y curl jq 
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version

# Install Node.js dependencies
RUN apt-get update && apt-get install -y gnupg \
  && curl -fsSL https://deb.nodesource.com/setup_14.x | bash - \
  && apt-get install -y graphviz \
  && apt-get clean && rm -rf /var/lib/apt/lists/* \ 
  && npm install -g aws-cdk redoc-cli

# Install Python dependencies
RUN pip install --upgrade pip \
  && pip install pyyaml pytest-html coverage awscli boto3==1.33.2 botocore==1.33.2 \ 
  && pip install -r base-requirements.txt \ 
  && pip install lambda-forge
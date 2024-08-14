FROM python:3.9-slim

WORKDIR /lambda-forge

COPY . /lambda-forge

# Install nvm with Node.js and npm
ENV NODE_VERSION=16.13.0
RUN apt-get update \
  && apt-get install -y curl jq \
  && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION} \
  && nvm use v${NODE_VERSION} \
  && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"

# Fix Node.js permissions
RUN chmod +x /root/.nvm/versions/node/v${NODE_VERSION}/bin/node

# Update NPM to the latest version
RUN npm install -g npm@latest

# Install Node.js dependencies as root user
USER root
RUN npm install -g aws-cdk cdk-assets@2 redoc-cli

# Switch back to default user
USER node

# Install Python dependencies
RUN pip install --upgrade pip \
  && pip install pyyaml pytest-html coverage awscli boto3==1.33.2 botocore==1.33.2 \
  && pip install -r base-requirements.txt \
  && pip install lambda-forge

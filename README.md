

# Lambda Forge

<p align="center">
<img src="https://public-lambda-forge-logo.s3.us-east-2.amazonaws.com/wNSN2U7n9NiAKEItWlsrcdJ0RWFyZOmbNvsc6Kht84WsWVxuBz5O.png" width=500 > 
</p>

Lambda Forge is a powerful and flexible open-source framework written in Python designed to streamline the creation, management, and deployment of AWS Lambda functions. Built with ease of use and scalability in mind, Lambda Forge empowers developers to focus on writing code while automating the tedious aspects of serverless application management.

Read the complete documentation at: [https://docs.lambda-forge.com/](https://docs.lambda-forge.com/)

## Features

### CLI
Lambda Forge comes with a CLI tool named `FORGE`, designed to facilitate the creation and management of resources related to serverless projects.

### Easy Creation of Lambda Functions
Easily create Lambda functions within a modular and scalable architecture, following the Single Responsibility Principle and Dependency Injection.

### Creation of Authorizers
Effortlessly create authorizers to secure access to your Lambda functions.

### AWS Resource Management
Lambda Forge encapsulates several AWS services, providing dedicated classes to handle specific responsibilities. Each class is injected into Lambda functions to facilitate interaction with AWS resources.

### Lambda Layers
Lambda Forge simplifies working with Lambda Layers, whether they are external libraries or custom code created by the developer. It automatically installs custom code in the virtual environment as if it were an external library.

### Live Development
Lambda Forge deploys real AWS resources and connects them to your local environment, enabling hot reload and easy debugging of your Lambda functions.

<p align="center">
<img src="https://i.ibb.co/6sRcyxF/live-server.gif" width=500> 
</p>

### Multi-Stage Environments with Automatic CI/CD Pipelines
Lambda Forge provides multi-stage environments with automatic CI/CD pipelines on CodePipeline for each environment, ensuring complete isolation from each other.

#### Development
<p align="center">
<img src="https://docs.lambda-forge.com/home/images/updated-dev.png" width=500> 
</p>

#### Staging
<p align="center">
<img src="https://docs.lambda-forge.com/home/images/staging-success.png" width=500> 
</p>

#### Production
<p align="center">
<img src="https://docs.lambda-forge.com/home/images/prod-success.png" width=500> 
</p>

### Automatic Documentation
Lambda Forge automatically generates documentation for your project and let them available through an api gateway endpoint, as demonstrated below:

<div style="width: 100%; text-align: center;" align="center">

<table style="width: 100%; font-size: 16px;">
  <tr>
    <td><a href="https://byi76zqidj.execute-api.us-east-2.amazonaws.com/prod/swagger">Swagger</a></td>
    <td><a href="https://byi76zqidj.execute-api.us-east-2.amazonaws.com/prod/redoc">Redoc</a></td>
    <td><a href="https://byi76zqidj.execute-api.us-east-2.amazonaws.com/prod/diagram">Diagram</a></td>
  </tr>
  <tr>
    <td><a href="https://qkaer0f0q5.execute-api.us-east-2.amazonaws.com/staging/coverage">Coverage</a></td>
    <td><a href="https://qkaer0f0q5.execute-api.us-east-2.amazonaws.com/staging/tests?sort=result">Tests</a></td>
    <td><a href="https://api.lambda-forge.com/dev/wiki">Wiki</a></td>
  </tr>
</table>
</div>

### Architecture Diagram

Lambda Forge automatically tracks the triggers and invocations of your Lambda functions, generating a comprehensive diagram of your application.

<p align="center">
<img src="https://i.ibb.co/McYdKPD/diagram.png" width=400> 
</p>


## 🚀 Installing Lambda Forge

To install Lambda Forge, follow these steps:

```sh
pip install lambda-forge
```


## 📫 Contributing to Lambda Forge

To contribute to Lambda Forge, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push origin <project_name>/<location>`
5. Create the pull request.

Alternatively, see the GitHub documentation on [how to create a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## 📝 License

This project is licensed. See the [LICENSE](LICENSE.md) file for more details.

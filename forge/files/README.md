# README

## Introduction

This pipeline is an AWS CloudFormation stack created with the AWS CDK (Cloud Development Kit) to automate the deployment of code to production. The pipeline is designed to pull source code from a GitHub repository, build, test, and deploy the code to multiple environments.

## Lambda Functions

To establish a consistent directory structure and facilitate the proper organization and deployment of Lambda functions across every project, adhere to the following directory structure:

```
functions/
└── example/
    ├── __init__.py
    ├── config.py
    ├── integration.py
    ├── main.py
    ├── unit.py
    └── utils.py
```

In this structure, the `example` directory contains the code and configuration files for your Lambda function. The `__init__.py` file is an empty file that indicates that the directory should be treated as a Python package.

The file structure for a Lambda function is to have the source code in the `main.py` file and the entry point function named **lambda_handler**. The configuration for any resources used by the function should be placed in the `config.py` file, and helper functions should be placed in the `utils.py` file. By following this structure, it becomes easier to manage and maintain the codebase of the Lambda function.

It is important that the `main.py` file does not contain any functions other than the lambda_handler. Any other functions, if needed, should be placed in `utils.py` and imported into the `main.py` file. This ensures that the code base is modular and maintainable.

To configure the necessary AWS resources for your function, import the **Services** class from `infra/services/__init__.py` and use it on `config.py`. Finally, add your config class to the **LambdaStack** constructor in `infra/stacks/lambda_stack.py`. This will ensure that the necessary resources are provisioned when you deploy your function.

Additionally, if your function requires integration with other services, such as API Gateway or Dynamo DB, you can create integration tests in the `integration.py` file. Similarly, the `unit.py` file should contain unit tests for your main function and the helper functions.

Following this directory structure and best practices makes it easier to develop, manage, test and deploy your Lambda functions.

## Gaia

Following the structure mentioned in the previous section brings several benefits such as organization, modularity and maintainability in the long-run. However, it might not bring the best developer experience when creating multiple files for a simple lambda function. This is where Gaia comes in handy!

Gaia is a command-line interface (CLI) tool developed specifically for this project that simplifies the process of creating the required folder structure. With Gaia, you can easily create a lambda function with the required structure and all the necessary configurations needed for deployment by running just one command in your terminal.

Gaia is installed with all the other project dependencies by running the command:

`$ pip install -r requirements.txt`

Creating a new lambda function is easy with Gaia. Just run the following command:

`$ gaia create $FUNCTION_NAME --method $METHOD --description $DESCRIPTION`

This command creates the lambda folder structure and configures the lambda function with the specified name, http method and description.

Here is an example of what the folder structure will look like:

```
functions/
└── $FUNCTION_NAME/
    ├── __init__.py
    ├── config.py
    ├── integration.py
    ├── main.py
    └── unit.py
```

If you want to share code across multiple lambda functions in the same folder, simply add the `--belongs` flag and specify the folder name:

`$ gaia create $FUNCTION_NAME --method $METHOD --description $DESCRIPTION --belongs $FOLDER`

This will create the following folder structure:

```
functions/
└── $FOLDER/
    ├── __init__.py
    ├── $FUNCTION_NAME/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── integration.py
    │   ├── main.py
    │   └── unit.py
    └── utils/
        └── __init__.py
```

This command enables you to specify the folder to which the lambda function belongs, making it easy to share code across different functions.

Finally, if you want to see a list of available commands and their descriptions, simply run:

`$ gaia create --help`

## Pipeline

This framework automates the creation a pipeline on AWS with the following steps:

- **Coverage**: This step measures the amount of production code that is covered by unit tests. This step will fail if the percentage of coverage is below `80%`. If you're migrating legacy code from other CDKs, you can omit those files in the `.coveragerc` configuration file. However, when creating a new lambda function, it's best to strive for high code coverage right from the beginning to minimize the risk of future issues. You can access the generated coverage report by clicking on `Details -> Reports` on CodePipeline.

- **Generate Docs**: This step automatically generates Swagger and ReDoc docs for all endpoints. In order to do so, each lambda function must have a corresponding `Input` and `Output` dataclass defined in the same file. Once these dataclasses are defined, the documentation will be automatically deployed to the API Gateway and can be accessed on the endpoints `/docs/swagger` and `/docs/redoc`.

- **Integration Tests**: This step executes integration tests on the code to verify the behavior of the system as a whole. You can access the generated integration test report by clicking on `Details -> Reports` on CodePipeline.

- **Sonar Cloud**: This step serves as a quality gate for the code to mitigate potential bugs, code smells, and vulnerabilities. Its purpose is to ensure that the code adheres to high standards of quality and security.

- **Unit Tests**: This step executes unit tests on the code to verify the behavior of individual code components. You can access the generated unit test report by clicking on `Details -> Reports` on CodePipeline.

- **Validate Docs**: This step ensures that all lambda functions triggered by the API Gateway has the `Input` and `Output` dataclasses defined.

- **Validate Integration Tests**: This step ensures that all endpoints triggered by the API Gateway are covered by at least one integration test. It is mandatory to have at least one integration test for each function triggered by the API Gateway. To achieve this, use the custom decorator `@pytest.mark.integration` and specify the method and endpoint arguments to declare that the test covers a specific endpoint.

This is how the pipeline is going to look like on AWS:

<div style="text-align: center;">
<img src="https://i.imgur.com/5uf5zkn.jpeg" alt="Dev" width="900" height="500">
</div>

<div style="text-align: center;">
<img src="https://i.imgur.com/EntefXu.jpg" alt="Prod" width="900" height="700">
</div>

## Documentation

All Lambda functions connected to the API Gateway are automatically documented with Swagger.

To generate the documentation, you need to add an Input data class and an Output data class to your Lambda function, specifying the parameters to be generated. If you are using a parameter in the URL (path), you also need to provide a Path data class.

Below is a demonstration of the data classes with the supported documentation features.

    from dataclasses import dataclass
    from typing import List, Literal, Optional

    @dataclass
    class Path:
        id: str


    @dataclass
    class ExampleObject:
        name: str
        age: int


    @dataclass
    class Input:
        string_input: str
        int_input: int
        float_input: float
        boolean_input: bool
        list_input: List[str]
        object_input: ExampleObject
        literal_input: Literal["a", "b", "c"]
        optional_input: Optional[str]


    @dataclass
    class Output:
        message: str

Here is an example of how the documentation will look like:

<div style="text-align: center;">
<img src="https://i.imgur.com/vxAT8Tt.jpg" alt="Swagger" width="900" height="500">
</div>

## Alarms

In production environment, there is an alarm system that triggers an alarm and sends a warning message on the engineering channel in Slack whenever a lambda function raises an exception. This allows us to quickly identify and address any issues, minimizing any negative impact on our users and ensuring the smooth functioning of our systems.

`Please, do not wrap your code with a generic try/except block, otherwise the alarms won't work.`

This is an example of a test alarm sent on slack:

<div style="text-align: center;">
<img src="https://i.imgur.com/uergmpK.jpg" alt="Alarm" width="900" height="500">
</div>

## Versioning

The production code is automatically versioned, allowing for fast and seamless rollback to a previous working version in the event of any failure. This ensures high availability and reliability of our systems, and helps to minimize downtime and prevent any negative impact on our users.

## Pre-Commit

It's crucial to ensure consistent code quality and formatting in any project. To achieve this, it's highly recommended to install pre-commit hooks using the command `pre-commit install`. These hooks will be triggered automatically before each commit, allowing you to catch potential issues, linting, formatting and maintaining the code consistency throughout the project.

Waiting for the entire pipeline to build before seeing the output from the pre-stage steps can be frustrating and time-consuming. This is where pre-commit comes in handy. By using pre-commit, you can verify that the pre-stage steps are passing locally before deploying to development or production environments. This helps you catch errors early on in the development process, reducing the likelihood of encountering issues during deployment and making the development process more efficient.

## Sonar Cloud

If you are cloning this repo for the first time, you need to configure SonarCloud. Please follow these steps to do so:

1. Log in to your SonarCloud account at https://sonarcloud.io/projects.
2. Click the "+" button located on the top right corner of the page.
3. Select "Analyze New Project" from the dropdown menu.
4. In the "Organization" dropdown, choose "Entri" and select the repository you want to analyze.
5. Click on "Setup".
6. Under "Quality Gate", click on "Set New Code Definition".
7. Choose "Previous version" from the list of options.

## Configuration

The pipeline is configured by setting values in the `cdk.json` file. The configuration options include:

- `name`: the name of the application being deployed.
- `repo`: the name of the GitHub repository where the source code is hosted.
- `dev:arns`: arns for the development environment.
- `prod:arns`: arns for the production environment.

## Deployment

To deploy the pipeline, run `cdk deploy --all` in the command line from the directory containing the pipeline code. Once deployed, the pipeline will automatically detect changes to the source code in the GitHub repository and deploy to the appropriate environment.

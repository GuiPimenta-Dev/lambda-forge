from setuptools import setup, find_packages

setup(
    name="lambda_forge",
    version="1.0.546",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "attrs==22.1.0",
        "aws-cdk-lib>=2.0.0,<3.0.0",
        "constructs>=10.0.0,<11.0.0",
        "boto3==1.26.59",
        "click==8.1.3",
        "pytest==6.2.5",
        "coverage==7.2.3",
        "python-dotenv==1.0.1",
        "b-aws-websocket-api==2.0.0",
        "requests==2.31.0",
        "AWSIoTPythonSDK==1.5.4",
        "awslambdaric==2.0.11",
        "pyfiglet==1.0.2",
    ],
    include_package_data=True,
    package_data={
        "lambda_forge": [
            "builders/*",
            "builders/**/*",
            "scaffold/*",
            "scaffold/**/**",
            "scaffold/**/**/*",
            "resources/*",
        ],
    },
    author="Guilherme Alves Pimenta",
    author_email="guialvespimenta27@gmail.com",
    description="Lambda Forge is a framework to help you create lambda functions following a pre-defined structure.",
    entry_points={"console_scripts": ["forge=lambda_forge.cli:forge"]},
)

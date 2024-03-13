from setuptools import setup, find_packages

setup(
    name="lambda-forge",
    version="0.1.0",
    py_modules=["forge"],
    packages=find_packages(),
    install_requires=["click"],
    author="Guilherme Alves Pimenta",
    author_email="guialvespimenta27@gmail.com",
    description="Lambda Forge is a cli tool to help you create new lambda functions following a pre-defined structure.",
    entry_points={"console_scripts": ["forge=scaffold.forge:forge"]},
)

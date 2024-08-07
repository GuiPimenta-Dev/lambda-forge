from aws_cdk import Stack
from constructs import Construct

from authorizers.secret.config import SecretAuthorizerConfig
from functions.rag.ask_question.config import AskQuestionConfig
from functions.rag.ask_questions.config import AskQuestionsConfig
from functions.rag.create_vectors.config import CreateVectorsConfig
from functions.rag.textual.config import TextualConfig
from functions.web_crawler.crawler.config import CrawlerConfig
from functions.web_crawler.start.config import StartConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        SecretAuthorizerConfig(self.services)

        # Web Crawler
        StartConfig(self.services)
        CrawlerConfig(self.services)

        # Rag
        AskQuestionConfig(self.services)
        AskQuestionsConfig(self.services)
        CreateVectorsConfig(self.services)
        TextualConfig(self.services)

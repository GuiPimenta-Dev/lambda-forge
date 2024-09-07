from authorizers.jwt.config import JwtAuthorizerConfig
from authorizers.sso.config import SSOAuthorizerConfig
from aws_cdk import Stack
from constructs import Construct
from docs.config import DocsConfig
from functions.auth.hello.config import HelloConfig
from functions.auth.signin.config import SigninConfig
from functions.auth.signup.config import SignupConfig
from functions.blog.comment_post.config import CommentPostConfig
from functions.blog.create_post.config import CreatePostConfig
from functions.blog.delete_comment.config import DeleteCommentConfig
from functions.blog.delete_post.config import DeletePostConfig
from functions.blog.feed.config import FeedConfig
from functions.blog.like_post.config import LikePostConfig
from functions.blog.update_post.config import UpdatePostConfig
from functions.chat.connect.config import ConnectConfig
from functions.chat.send_connection_id.config import SendConnectionIdConfig
from functions.chat.send_message.config import SendMessageConfig
from functions.guess_the_number.create_game.config import CreateGameConfig
from functions.guess_the_number.make_guess.config import MakeGuessConfig
from functions.images.mailer.config import MailerConfig
from functions.images.qrcode.config import QrcodeConfig
from functions.urls.redirect.config import RedirectConfig
from functions.urls.shortener.config import ShortenerConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        SSOAuthorizerConfig(self.services)
        JwtAuthorizerConfig(self.services)

        # Docs
        DocsConfig(self.services)

        # GuessTheNumber
        MakeGuessConfig(self.services)
        CreateGameConfig(self.services)

        # Urls
        RedirectConfig(self.services)
        ShortenerConfig(self.services, context)

        # Images
        MailerConfig(self.services)
        QrcodeConfig(self.services)

        # Auth
        HelloConfig(self.services)
        SigninConfig(self.services)
        SignupConfig(self.services)

        # Chat
        SendMessageConfig(self.services, context)
        SendConnectionIdConfig(self.services, context)
        ConnectConfig(self.services)

        # Blog
        DeletePostConfig(self.services)
        UpdatePostConfig(self.services)
        LikePostConfig(self.services)
        DeleteCommentConfig(self.services)
        CommentPostConfig(self.services)
        FeedConfig(self.services)
        CreatePostConfig(self.services)

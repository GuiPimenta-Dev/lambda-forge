from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_iam as iam
from aws_cdk import pipelines as pipelines


class CodeBuild:
    def __init__(self, scope, context, source) -> None:
        self.scope = scope
        self.context = context
        self.source = source

    def create_step(
        self,
        name,
        commands,
        docker_registry="public.ecr.aws/x8r4y7j7/lambda-forge:latest",
        install_commands=[],
        env={},
        partial_build_spec={},
        permissions=[],
        requirements="requirements.txt",
    ):

        return pipelines.CodeBuildStep(
            name,
            input=self.source,
            install_commands=[
                "cp -r /lambda-forge/* .",
                "forge layer --install",
                f"pip install -r {requirements}",
                *install_commands,
            ],
            env=env,
            commands=commands,
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_docker_registry(docker_registry),
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables=env,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(partial_build_spec),
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            role_policy_statements=[*self.get_role_policy_statements(permissions)],
        )

    @staticmethod
    def get_role_policy_statements(permissions):

        ECR_PERMISSIONS = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["ecr:*"],
            resources=["*"],
        )

        role_policy_statements = [ECR_PERMISSIONS]
        for role in permissions:
            role_policy_statements.append(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=role["actions"],
                    resources=role["resources"],
                )
            )

        return role_policy_statements

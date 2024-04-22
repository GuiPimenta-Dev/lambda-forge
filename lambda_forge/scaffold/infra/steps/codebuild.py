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
        install_commands=[],
        env={},
        partial_build_spec={},
        permissions=[],
        requirements="requirements.txt",
    ):

        PUBLIC_ECR = "public.ecr.aws/x8r4y7j7/lambda-forge:latest"

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
                build_image=codebuild.LinuxBuildImage.from_docker_registry(PUBLIC_ECR),
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables=env,
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(partial_build_spec),
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            role_policy_statements=[*self.get_role_policy_statements(permissions)],
        )

    def create_report_group(self, name, files, file_format, base_directory=".", coverage=False):
        report_type = codebuild.ReportGroupType.CODE_COVERAGE if coverage else codebuild.ReportGroupType.TEST
        report_group = codebuild.ReportGroup(
            self.scope, f"{self.context.stage}-{self.context.name}-{name}", type=report_type
        )

        report_group_build_spec = {
            "reports": {
                report_group.report_group_arn: {
                    "files": files,
                    "base-directory": base_directory,
                    "file-format": file_format,
                }
            },
        }

        report_group_permissions = [
            {
                "actions": [
                    "codebuild:CreateReportGroup",
                    "codebuild:CreateReport",
                    "codebuild:UpdateReport",
                    "codebuild:BatchPutTestCases",
                    "codebuild:BatchPutCodeCoverages",
                ],
                "resources": [report_group.report_group_arn],
            }
        ]

        return report_group_build_spec, report_group_permissions

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

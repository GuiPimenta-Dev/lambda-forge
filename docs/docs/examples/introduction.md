In this guide, we'll take you on a journey through the development process with Lambda Forge, illustrating the progression of projects through a hands-on, step-by-step approach within a unified codebase. Our methodology employs an incremental build strategy, where each new feature enhances the foundation laid by preceding projects, ensuring a cohesive and scalable architecture without duplicating efforts.

To keep our focus sharp on AWS resources and Lambda Forge architecture, we'll skip over the detailed discussion of unit and integration tests here. However, for those eager to dive deeper into testing methodologies, there is an insightful article called [Mocking AWS Resources for Unit Testing](https://docs.lambda-forge.com/articles/page3) aimed at enriching your understanding about the subject.

Our objective is to provide a streamlined and informative learning path, striking a balance between technical detail and approachability to keep you engaged without feeling overwhelmed.

To enhance usability and the overall user experience, we've implemented a custom domain, `https://api.lambda-forge.com`, making our URLs succinct and memorable across various deployment stages:

- **Dev** - `https://api.lambda-forge.com/dev`
- **Staging** - `https://api.lambda-forge.com/staging`
- **Prod** - `https://api.lambda-forge.com`

For those interested in customizing domain names within API Gateway, the [How to Configure a Custom Domain Name for API Gateway](https://docs.lambda-forge.com/articles/page2) guide offers a detailed tutorial on personalizing your project's URL.

With that being said, let's forge some Lambdas!

```
forge project lambda-forge-examples --repo-owner "$GITHUB-OWNER" --repo-name "$GITHUB-REPO" --bucket "$S3-BUCKET"
```

**Docs**: [https://api.lambda-forge.com/docs](https://examples.lambda-forge.com/docs).

**Source code**: [https://github.com/GuiPimenta-Dev/lambda-forge-examples](https://github.com/GuiPimenta-Dev/lambda-forge-examples)

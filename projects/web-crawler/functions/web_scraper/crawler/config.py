from infra.services import Services


class CrawlerConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Crawler",
            path="./functions/web_scraper",
            directory="crawler",
            description="crawl the websites",
            dead_letter_queue_enabled=True,
            dead_letter_queue=services.sqs.crawler_queue_dlq,
            layers=[services.layers.requests_layer, services.layers.bs4_layer],
            environment={
                "VISITED_URLS_TABLE_NAME": services.dynamodb.visited_urls_table.table_name,
                "CRAWLER_QUEUE_URL": services.sqs.crawler_queue.queue_url,
            },
        )

        services.sqs.create_trigger("crawler_queue", function)

        services.dynamodb.grant_write("visited_urls_table", function)
        services.dynamodb.visited_urls_table.grant_read_data(function)

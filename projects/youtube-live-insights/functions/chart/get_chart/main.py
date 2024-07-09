import json
import os
from dataclasses import dataclass
from typing import List, Optional
import boto3

from . import utils

@dataclass
class Input:
    video_id: str
    interval: Optional[int] = 10


@dataclass
class Video:
    publish_date: str
    url: str
    duration: str
    language: str
    title: str


@dataclass
class ChatData:
    chat_summary: str
    rating: int
    reason: str
    messages: List[str]
    

@dataclass
class Output:
    video: Video
    data: List[ChatData]



def lambda_handler(event, context):

    video_id = event["queryStringParameters"]["video_id"]
    interval = int(event["queryStringParameters"].get("interval", 10))

    dynamodb = boto3.resource("dynamodb")
    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME")
    VIDEOS_TABLE_NAME = os.environ.get("VIDEOS_TABLE_NAME", "Dev-Videos")

    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)
    videos_table = dynamodb.Table(VIDEOS_TABLE_NAME)

    video = videos_table.get_item(Key={"PK": video_id})["Item"]

    data = utils.query_all_items(transcriptions_table, video_id, interval)
    data = utils.subtract_hours_from_utc(data, hour=3)

    data = {"video": video, "data": data}
    print(data)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat Rating Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f4f4f9;
            }}
            #chart-container {{
                width: 80%;
                max-width: 1200px;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            canvas {{
                width: 100% !important;
                height: auto !important;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            <canvas id="ratingChart"></canvas>
        </div>
        <script>
            const data = {json.dumps(data["data"], default=str)};

            const labels = data.map(item => item.hour);
            const ratings = data.map(item => parseInt(item.rating));

            const chartData = {{
                labels: labels,
                datasets: [{{
                    label: 'Chat Ratings',
                    data: ratings,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 1
                }}]
            }};

            const config = {{
                type: 'line',
                data: chartData,
                options: {{
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'Hour'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'Rating'
                            }},
                            beginAtZero: true,
                            max: 10
                        }}
                    }}
                }}
            }};

            const ratingChart = new Chart(
                document.getElementById('ratingChart'),
                config
            );
        </script>
    </body>
    </html>
    """

    return {
        "statusCode": 200,
        "body": html_content,
        "headers": {"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"},
    }
import requests, os
import structlog
import asyncio

logger = structlog.get_logger()

class SlackAPI(object):
    """ This class is used to create a Slack channel for a student team """
    def __init__(self):
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

    async def send_message(self, channel, text):
        # Configure the config for the Slack message
        channel_payload = {
            "text": text,
            "token": os.getenv("SLACK_BOT_TOKEN"),
            "channel": channel
        }

        try:
            response = requests.post(
                url="https://slack.com/api/chat.postMessage",
                data=channel_payload,
                headers=self.headers,
                timeout=10
            )
            logger.info("slack.message_sent", channel=channel)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("slack.message_failed", channel=channel, error=str(e))
            raise

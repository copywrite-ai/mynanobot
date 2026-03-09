import asyncio
import json
import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from ..logger import logger
from ..i18n import i18n

class SlackConnector:
    """Slack connector using Socket Mode, similar to FeishuConnector."""
    def __init__(self, bus, bot_token, app_token):
        self.bus = bus
        self.bot_token = bot_token
        self.app_token = app_token
        self.web_client = AsyncWebClient(token=bot_token)
        self.socket_client = SocketModeClient(
            app_token=app_token,
            web_client=self.web_client
        )
        self.loop = None
        self._running = False

    async def start(self):
        self.loop = asyncio.get_running_loop()
        self._running = True
        
        # Register event handler
        self.socket_client.socket_mode_request_listeners.append(self._process_request)
        
        logger.info(i18n["slack_starting"])
        await self.socket_client.connect()
        logger.info(i18n["slack_init"])

    async def _process_request(self, client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            # Acknowledge the request immediately
            response = SocketModeResponse(envelope_id=req.envelope_id)
            await client.send_socket_mode_response(response)

            # Handle message events
            event = req.payload.get("event", {})
            if event.get("type") == "message" and "bot_id" not in event:
                await self._on_message(event)

    async def _on_message(self, event):
        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text", "")
        message_ts = event.get("ts")
        
        logger.info(i18n["slack_msg_received"].format(user=user_id, channel=channel_id, text=text, ts=message_ts))
        
        # Add a reaction as confirmation (like Feishu's THUMBSUP)
        await self._send_reaction(channel_id, message_ts, "eyes")
        
        await self.bus.inbound.put({
            "channel": "slack",
            "sender": channel_id, # Using channel_id as sender for Slack (similar to Feishu open_id)
            "user_id": user_id,
            "text": text,
            "message_id": message_ts,
            "channel_type": event.get("channel_type")
        })

    async def _send_reaction(self, channel_id: str, timestamp: str, emoji_name: str):
        """Add a reaction to a message."""
        try:
            await self.web_client.reactions_add(
                name=emoji_name,
                channel=channel_id,
                timestamp=timestamp
            )
        except Exception as e:
            logger.warning(i18n["slack_reaction_fail"].format(e=e))

    async def watch_outbound(self):
        while True:
            msg = await self.bus.outbound.get()
            channel_id = msg["sender"]
            message_ts = msg.get("message_id")
            status = msg.get("status")
            text = msg.get("text", "")

            # Handle status reactions
            if message_ts:
                if status == "processing":
                    # Potentially show 'typing' or another reaction
                    pass 
                elif status == "finished":
                    await self._send_reaction(channel_id, message_ts, "white_check_mark")
                elif status == "error":
                    await self._send_reaction(channel_id, message_ts, "x")

            # Send message if text is present
            if text:
                try:
                    # Parse markdown/formatting if needed (Slack uses its own, but supports basics)
                    await self.web_client.chat_postMessage(
                        channel=channel_id,
                        text=text,
                        unfurl_links=False,
                        unfurl_media=False
                    )
                    logger.info(i18n["slack_send_success"].format(channel=channel_id))
                except Exception as e:
                    logger.error(i18n["slack_send_fail"].format(e=e))

if __name__ == "__main__":
    # Test script similar to Feishu
    async def test_slack():
        from nanocore.bus import MessageBus
        from dotenv import load_dotenv
        load_dotenv()
        
        bus = MessageBus()
        BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
        APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
        
        if not BOT_TOKEN or not APP_TOKEN:
            print("Please set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in .env")
            return

        slack = SlackConnector(bus, BOT_TOKEN, APP_TOKEN)
        
        async def watch():
            while True:
                msg = await bus.inbound.get()
                print(f"📥 [Slack Test] Received: {msg['text']}")
                await bus.outbound.put({
                    "sender": msg["sender"], 
                    "message_id": msg["message_id"],
                    "text": f"Got it! You said: {msg['text']}",
                    "status": "finished"
                })

        await asyncio.gather(slack.start(), slack.watch_outbound(), watch())

    asyncio.run(test_slack())

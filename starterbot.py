import os
import time
import re
from slackclient import SlackClient
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import signal

cwd = os.getcwd()

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


"""Setting up logger"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(
    'slackbot.log', mode='a', maxBytes=5*1024*1024, backupCount=2,
    encoding=None, delay=0)
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(threadName)s:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
running_flag = True
EXIT_COMMAND = "exit"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
Should_run = True
GREETING = False


def receive_signal(signum, stack):
    """Logs Interrupt and Termination signals"""
    logger.warning("Received signal: {}".format(signum))
    global running_flag
    if signum == signal.SIGINT:
        running_flag = False
    if signum == signal.SIGTERM:
        running_flag = False


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM
        API to find bot commands.
        If a bot command is found, this function returns a tuple
         of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]

    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message
        text and returns the user ID which was mentioned. If there is no direct
        mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the
    # remaining message
    return(matches.group(1),
           matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    greeting = """Oh, Hi There! <3 My name is giffany. I am a school girl at
                School university. \n Will you help me carry my books?"""
    # Default response is help text for the user

    response = None

    # images and gifs
    greeting_img = "file:/" + cwd + "/imgs/talking.gif"
    print(greeting_img)
    global GREETING
    # Sends the response back to the channel
    if not GREETING:

        attachments = [{"title": "Hello!", "image_url": greeting_img}]
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text='',
            attachments=attachments
        )
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=greeting,

        )

    else:
        if command.startswith("yes" or "sure" or "why not"):
            response = """Awww ~ :heart: Thank you! \n ...now you're my
                        boyfriend"""
        if command.startswith(EXIT_COMMAND):
            global Should_run
            Should_run = False
            response = "Bye ~ :heart: :knife: "
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )
        logger.info(response)

    GREETING = True


def readsc():
    """inner reading loop"""
    while running_flag and Should_run:
        command, channel = parse_bot_commands(slack_client.rtm_read())
        if command:
            handle_command(command, channel)
        time.sleep(1)


def main():
    global starterbot_id
    signal.signal(signal.SIGINT, receive_signal)
    signal.signal(signal.SIGTERM, receive_signal)
    start_time = time.time()
    while running_flag and Should_run:
        if slack_client.rtm_connect(with_team_state=False):
            # starterbot's user ID in Slack: value is assigned after the bot
            # starts up
            starterbot_id = slack_client.api_call("auth.test")["user_id"]
            logger.info("Giffany Online")
            logger.info("Starter Bot connected and running!")
            try:
                readsc()
            except Exception:
                logger.exception(Exception)
                logger.info("restarting")
                time.sleep(5)
        logger.info("Giffany Offline - uptime: {} seconds.".format(
            time.time() - start_time))


if __name__ == "__main__":
    main()

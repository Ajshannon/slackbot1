import unittest
import slackbot

greeting = """Oh, Hi There! <3 My name is giffany. I am a school girl at
                School university. \n Will you help me carry my books?"""


class slackbotTest(unittest.TestCase):
    def test_handle(self):
        """tests the greeting"""
        self.assertEqual(
            slackbot.handle_command('hello', "channel"),
            greeting)


if __name__ == '__main__':
    unittest.main()

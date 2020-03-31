import unittest
import app
from time import time
import json
import hmac
import hashlib

class TestServer(unittest.TestCase):

    def setUp(self):
        self.client = app.app.test_client()
        self.client.testing = True
        self.time = time()

    def generate_signature(self, request_data):
        encoded_request = str.encode('v0:' + str(int(self.time)) + ':' + request_data)
        hashed_request = 'v0=' + hmac.new(
                str.encode('a'),
                encoded_request,
                hashlib.sha256
            ).hexdigest()
        return hashed_request

    def test_404(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_data(), b"These are not the slackbots you're looking for.")
    
    def test_200(self):
        request_data = json.dumps({'event': {'type':'message', 'text': 'Test text', 'channel':'0', 'ts':'1'}})
        signature = self.generate_signature(request_data)
        response = self.client.post(
            "/",
            data=request_data,
            headers={
                "X-Slack-Request-Timestamp": int(self.time),
                "X-Slack-Signature": signature
                }
        )
        self.assertEqual(response.status_code, 200)

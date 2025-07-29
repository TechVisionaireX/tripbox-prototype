import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_hello_route(self):
        response = self.app.get('/api/hello')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "Hello from backend!"})

    def test_404_route(self):
        response = self.app.get('/api/unknown')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()

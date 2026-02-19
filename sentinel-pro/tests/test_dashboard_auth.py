import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestDashboardAuth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_logs_unauthorized(self):
        print("Testing /api/dashboard/logs unauthorized access...")  
        response = self.client.get("/api/dashboard/logs")
        self.assertEqual(response.status_code, 401)
        print("Passed: Received 401 Unauthorized")

    def test_dashboard_status_unauthorized(self):
        print("Testing /api/dashboard/status unauthorized access...")
        response = self.client.get("/api/dashboard/status")
        self.assertEqual(response.status_code, 401)
        print("Passed: Received 401 Unauthorized")

if __name__ == '__main__':
    unittest.main()

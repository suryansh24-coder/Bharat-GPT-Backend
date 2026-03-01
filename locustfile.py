from locust import HttpUser, task, between
import json

class BharatGPTUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """Register and Login on startup to get a JWT token"""
        self.email = f"loadtest_{self.environment.runner.client_id}@test.local"
        self.password = "secure_load_test"
        
        # We attempt to register but ignore if exists
        self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": "Load Test User"
        }, catch_response=True)
        
        # Login
        response = self.client.post("/api/v1/auth/login", data={
            "username": self.email,
            "password": self.password
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(3)
    def test_health_check(self):
        self.client.get("/health")

    @task(5)
    def test_list_conversations(self):
        if hasattr(self, 'headers') and self.headers:
            self.client.get("/api/v1/chat/conversations", headers=self.headers)

    @task(1)
    def test_chat_stream(self):
        if hasattr(self, 'headers') and self.headers:
            payload = {
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "mode": "Standard"
            }
            # Stream response parsing for locust
            with self.client.post("/api/v1/chat/stream", json=payload, headers=self.headers, stream=True, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Stream failed with {response.status_code}")

from locust import HttpUser, task


class ServerPerfTest(HttpUser):
    @task
    def index(self):
        self.client.get("/")

    @task
    def login(self):
        self.client.post("/showSummary", {"email": "john@simplylift.co"})

    @task
    def logout(self):
        self.client.get("/logout")

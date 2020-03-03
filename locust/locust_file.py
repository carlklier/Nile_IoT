from locust import HttpLocust, TaskSet, task, between
import pts_lib

pts_lib.launch_pts("localhost")

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        #self.login()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        #self.logout()

    def login(self):
        self.client.post("/login", {"username":"ellen_key", "password":"education"})

    def logout(self):
        self.client.post("/logout", {"username":"ellen_key", "password":"education"})

    @task(1)
    def index(self):
        self.client.get("/")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(1, 3)

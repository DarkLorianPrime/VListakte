import random
import string
import unittest

from httpx import ConnectError

from libraries.utils.tests import CustomClient

usernames = []
tokens = []
blogs = []
password = "11223344"


class TestAPI(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.client = CustomClient(base_url="http://127.0.0.1:8000/api/v1/")
            self.client.get("")
        except ConnectError:
            print('error_main')

    def generate_username(self):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(20))

    def test_1_registration_successful(self):
        user_1 = self.generate_username()
        user_2 = self.generate_username()

        response = self.client.post("registration/", data={"username": user_1, "password": password})
        assert response.status_code == 201

        response = self.client.post("registration/", data={"username": user_2, "password": password})
        assert response.status_code == 201

        usernames.extend([user_1, user_2])

    def test_2_registration_error(self):
        response = self.client.post("registration/", data={"username": usernames[0], "password": password})
        response_json = response.json()
        assert response.status_code == 422
        assert response_json.get("detail") == "Username already exists"

    def test_3_auth_no_params(self):
        response = self.client.post("login/")
        response_json = response.json()
        assert response.status_code == 422
        assert response_json.get("detail") is not None
        assert len(response_json.get("detail", [])) == 2

    def test_4_auth_one_params(self):
        response = self.client.post("login/", data={"username": usernames[0]})
        response_json = response.json()
        assert response.status_code == 422
        assert response_json.get("detail") is not None
        assert len(response_json.get("detail", [])) == 1

    def test_5_auth_successful(self):
        response = self.client.post("login/", data={"username": usernames[0], "password": password})
        response_json = response.json()
        assert response.status_code == 200
        token = response_json.get("access_token", None)
        assert token is not None
        tokens.append(token)

        response = self.client.post("login/", data={"username": usernames[1], "password": password})
        response_json = response.json()
        assert response.status_code == 200
        {}.get()
        token = response_json.get("access_token", None)
        assert token is not None
        tokens.append(token)

    def test_6_auth_error(self):
        response = self.client.post("login/", data={"username": usernames[0] + "a", "password": password})
        response_json = response.json()
        assert response.status_code == 404
        assert response_json.get("detail") == "Username or password not found"

    def test_7_auth_error_invalid_password(self):
        response = self.client.post("login/", data={"username": usernames[0], "password": password + "a"})
        response_json = response.json()
        assert response.status_code == 404
        assert response_json.get("detail") == "Username or password not found"

    def test_8_create_blog_user_1(self):
        response = self.client.post("/", data={"title": "blog_1",
                                               "description": "blog_1 description",
                                               "authors": "1,2"},
                                    headers={"authorization": f"token {tokens[0]}"})
        response_json = response.json()
        assert response.status_code == 201
        assert isinstance(response_json["id"], str)
        assert response_json["authors"] == [1, 2]
        blogs.append(response_json["id"])

    def test_9_create_blog_user_2(self):
        response = self.client.post("/", data={"title": "blog_2",
                                               "description": "blog_2 description",
                                               "authors": "1,2"},
                                    headers={"authorization": f"token {tokens[1]}"})
        response_json = response.json()
        assert response.status_code == 201
        assert isinstance(response_json["id"], str)
        assert response_json["authors"] == [1, 2]
        blogs.append(response_json["id"])

    def test_10_create_post(self):
        response = self.client.post(f"/{blogs[0]}/", data={"title": "post_1",
                                                           "text": "description"},
                                    headers={"authorization": f"token {tokens[0]}"})
        response_json = response.json()


if __name__ == "__main__":
    unittest.main(verbosity=0)

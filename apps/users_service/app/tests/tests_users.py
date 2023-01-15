import requests
from . settings import ExtendedRequest
from . tests_auth import TestsAuthUtils, TOKEN_NOT_VALID


ROUTE = "users"

USER_REGISTRATION_DATA = {
    "email": "am.darski@test.com",
    "username": "am.darski@test.com",
    "name": "Adam",
    "lastname": "Darski",
    "password": 'testtest11&@test',
    "is_2fa": False
}

CUSTOMER_DATA = {
    "id": 2,
    "email": "dv.gahan@test.com",
    "username": "dv.gahan@test.com",
    "name": "Dave",
    "lastname": "Gahan",
    "is_admin": False,
    "is_2fa": False,
    "is_active": True,
    "full_name": "Dave Gahan"
}


class TestsUsersUtils:
    @classmethod
    def customer_login(cls) -> dict:
        return cls.extract_token(TestsAuthUtils.customer_login())

    @classmethod
    def admin_login(cls) -> dict:
        return cls.extract_token(TestsAuthUtils.admin_login_otp_verified())

    @staticmethod
    def invalid_token() -> dict:
        return {
            "Authorization": f"bearer token-invalid"
        }

    @staticmethod
    def temporary_token() -> dict:
        response = TestsAuthUtils.admin_login()
        data = response.json()
        return {
            "Authorization": f"{data.get('token_type')} {data.get('temporary_token')}"
        }

    @staticmethod
    def extract_token(response:requests.Response) -> dict:
        data = response.json()
        return {
            "Authorization": f"{data.get('token_type')} {data.get('access_token')}",
        }

    @staticmethod
    def compare_dicts(dict_a: dict, dict_b:dict, keys: list = None) -> None:
        if not keys:
            keys = dict_a.keys()
        for key in keys:
            assert dict_a.get(key) == dict_b.get(key)


def test_registration_success():
    response = ExtendedRequest().make_post(url=f"{ROUTE}/registration", json=USER_REGISTRATION_DATA)
    assert response.status_code == 200
    # check data output
    user_data = USER_REGISTRATION_DATA.copy()
    user_data["is_admin"] = False
    user_data["full_name"] = "Adam Darski"
    data = response.json()
    TestsUsersUtils.compare_dicts(
        user_data,
        data,
        ["email", "username", "name", "lastname", "full_name", "is_2fa", "is_admin"]
    )


def test_registration_duplicate_username_failed():
    response = ExtendedRequest().make_post(f"{ROUTE}/registration", json=USER_REGISTRATION_DATA)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "User already exists"
    }


def test_registration_invalid_email_fail():
    user_data = USER_REGISTRATION_DATA.copy()
    user_data["email"] = "invalid-email"
    response = ExtendedRequest().make_post(f"{ROUTE}/registration", json=user_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Email not valid"
    }


def test_registration_invalid_password_fail():
    user_data = USER_REGISTRATION_DATA.copy()
    user_data["password"] = "1"
    response = ExtendedRequest().make_post(f"{ROUTE}/registration", json=user_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Password must be length at least 8 characters"
    }


def test_me_success():
    headers = TestsUsersUtils.customer_login()
    response = ExtendedRequest().make_get(f"{ROUTE}/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    TestsUsersUtils.compare_dicts(
        CUSTOMER_DATA, data
    )


def test_me_invalid_token_failed():
    headers = TestsUsersUtils.invalid_token()
    response = ExtendedRequest().make_get(f"{ROUTE}/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == TOKEN_NOT_VALID


def test_me_temporary_token_failed():
    headers = TestsUsersUtils.temporary_token()
    response = ExtendedRequest().make_get(f"{ROUTE}/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == TOKEN_NOT_VALID


def test_retrieve_success():
    headers = TestsUsersUtils.admin_login()
    response = ExtendedRequest().make_get(
        f"{ROUTE}/?user_id={CUSTOMER_DATA.get('id')}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    TestsUsersUtils.compare_dicts(
        CUSTOMER_DATA, data[0]
    )


def test_list_success():
    headers = TestsUsersUtils.admin_login()
    response = ExtendedRequest().make_get(f"{ROUTE}/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_retrieve_list_by_customer_failed():
    headers = TestsUsersUtils.customer_login()
    response = ExtendedRequest().make_get(f"{ROUTE}/?user_id=1", headers=headers)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Not enough permissions"
    }


def test_customer_update_profile_success():
    headers = TestsUsersUtils.customer_login()
    response = ExtendedRequest().make_patch(f"{ROUTE}/",json={"name": "Martin"},headers=headers)
    assert response.status_code == 200
    assert response.json().get("name") == "Martin"
    ExtendedRequest().make_patch(f"{ROUTE}/",json={"name": "Dave"},headers=headers)


def test_admin_update_customer_profile_success():
    headers = TestsUsersUtils.admin_login()
    response = ExtendedRequest().make_patch(
        f"{ROUTE}/?user_id=2",
        json={"name": "Martin"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json().get("name") == "Martin"
    ExtendedRequest().make_patch(
        f"{ROUTE}/?user_id=2",
        json={"name": "Dave"},
        headers=headers
    )


def test_customer_update_other_customer_profile_failed():
    headers = TestsUsersUtils.customer_login()
    response = ExtendedRequest().make_patch(
        f"{ROUTE}/?user_id=2",
        json={"name": "Martin"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json().get("name") == "Martin"
    ExtendedRequest().make_patch(
        f"{ROUTE}/?user_id=2",
        json={"name": "Dave"},
        headers=headers
    )


def test_customer_change_password_succes():
    password_data = {
        "password": "newpassword123@",
        "confirm_password": "newpassword123@"
    }
    headers = TestsUsersUtils.customer_login()
    response = ExtendedRequest().make_post(f"{ROUTE}/change-password", json=password_data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Password updated"
    }
    credentials = {
        "username": "dv.gahan@test.com",
        "password": "newpassword123@"
    }
    response = ExtendedRequest().make_post(f"auth/token", data=credentials)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()
    password_data = {
        "password": "testtest11&@",
        "confirm_password": "testtest11&@"
    }
    ExtendedRequest().make_post(f"{ROUTE}/change-password", json=password_data, headers=headers)


def test_customer_change_password_failed():
    password_data = {
        "password": "psin",
        "confirm_password": "psin"
    }
    headers = TestsUsersUtils.customer_login()
    response = ExtendedRequest().make_post(f"{ROUTE}/change-password", json=password_data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Password must be length at least 8 characters"
    }


def test_customer_delete_profile_success():
    response = ExtendedRequest().make_post(f"auth/token", data=USER_REGISTRATION_DATA)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()
    headers = TestsUsersUtils.extract_token(response)
    response = ExtendedRequest().make_delete(f"{ROUTE}/", headers=headers)
    assert response.status_code == 200
    response = ExtendedRequest().make_post(f"auth/token", data=USER_REGISTRATION_DATA)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


def test_admin_delete_customer_success():
    headers = TestsUsersUtils.admin_login()
    response = ExtendedRequest().make_delete(
        f"{ROUTE}/?user_id={CUSTOMER_DATA.get('id')}", headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"User with id:'{CUSTOMER_DATA.get('id')}' deleted successfully"
    }
    # search user
    response = ExtendedRequest().make_get(
        f"{ROUTE}/?user_id={CUSTOMER_DATA.get('id')}", headers=headers
    )
    assert response.status_code == 200
    assert response.json() == []

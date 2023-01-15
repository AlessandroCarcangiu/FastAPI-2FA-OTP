import os
import requests
from . settings import ExtendedRequest


ROUTE = "auth"
FAKE_EMAIL = f"{os.path.join(os.path.dirname(__file__))}/../logs/otp-logs.txt"


TOKEN_NOT_VALID = {
        "detail": "Token not valid"
}


class TestsAuthUtils:
    @classmethod
    def customer_login(cls) -> requests.Response:
        USER_WITH_2FA_DISABLED = {
            "username": "dv.gahan@test.com",
            "password": "testtest11&@"
        }
        return cls.__login(USER_WITH_2FA_DISABLED)

    @classmethod
    def admin_login(cls) -> requests.Response:
        USER_WITH_2FA_ENABLED = {
            "username": "rs.smith@test.com",
            "password": "testtest11&@admin"
        }
        return cls.__login(USER_WITH_2FA_ENABLED)

    @classmethod
    def admin_login_otp_verified(cls) -> requests.Response:
        response = TestsAuthUtils.admin_login()
        resp_json = response.json()
        temporary_token = resp_json.get("temporary_token")
        token_type = resp_json.get("token_type")
        otp = TestsAuthUtils.get_otp()
        return ExtendedRequest().make_post(
            url=f"{ROUTE}/verify-otp",
            headers={"Authorization": f"{token_type} {temporary_token}"},
            json={"otp": otp}
        )

    @staticmethod
    def __login(credentials: dict) -> requests.Response:
        return ExtendedRequest().make_post(f"{ROUTE}/token", data=credentials)

    @staticmethod
    def get_otp() -> str:
        with open(FAKE_EMAIL, "r") as f:
            return f.read().split("/")[-1]


def test_login_with_2fa_disabled_success():
    # login
    response = TestsAuthUtils.customer_login()
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()
    # verify token
    access_token = response.json().get("access_token")
    token_type = response.json().get("token_type")
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/verify-token",
        headers={"Authorization": f"{token_type} {access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": True
    }


def test_login_failed():
    USER_LOGIN_FAILED = {
        "username": "dv.gan@test.com",
        "password": "testtest"
    }
    response = ExtendedRequest().make_post(url=f"{ROUTE}/token", data=USER_LOGIN_FAILED)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


def test_login_with_2fa_enabled_success():
    # login
    response = TestsAuthUtils.admin_login()
    assert response.status_code == 200
    assert "temporary_token" in response.json()
    assert "token_type" in response.json()
    # verify otp
    temporary_token = response.json().get("temporary_token")
    token_type = response.json().get("token_type")
    otp = TestsAuthUtils.get_otp()
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/verify-otp",
        headers={"Authorization": f"{token_type} {temporary_token}"},
        json={"otp": otp}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()
    # verify token
    access_token = response.json().get("access_token")
    token_type = response.json().get("token_type")
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/verify-token",
        headers={"Authorization": f"{token_type} {access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": True
    }


def test_login_with_2fa_enabled_failed_by_token():
    response = TestsAuthUtils.admin_login()
    # verify otp
    temporary_token = "TOKEN-FALSE"
    token_type = response.json().get("token_type")
    otp = TestsAuthUtils.get_otp()
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/verify-otp",
        headers={"Authorization": f"{token_type} {temporary_token}"},
        json={"otp": otp}
    )
    assert response.status_code == 401
    assert response.json() == TOKEN_NOT_VALID


def test_login_with_2fa_enabled_failed_by_otp():
    response = TestsAuthUtils.admin_login()
    # verify otp
    temporary_token = response.json().get("temporary_token")
    token_type = response.json().get("token_type")
    otp = "12345678"
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/verify-otp",
        headers={"Authorization": f"{token_type} {temporary_token}"},
        json={"otp": otp}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "OTP not valid"
    }


def test_login_with_2fa_enabled_failed_by_disabled_otp():
    response = TestsAuthUtils.admin_login()
    # verify otp
    temporary_token = response.json().get("temporary_token")
    token_type = response.json().get("token_type")
    otp = TestsAuthUtils.get_otp()
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/verify-otp",
        headers={"Authorization": f"{token_type} {temporary_token}"},
        json={"otp": otp}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/verify-otp",
        headers={"Authorization": f"{token_type} {temporary_token}"},
        json={"otp": otp}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "OTP not valid"
    }


def test_refresh_token_success():
    response = TestsAuthUtils.customer_login()
    # refresh token
    refresh_token = response.json().get("refresh_token")
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/refresh-token",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()


def test_refresh_token_failed():
    # refresh token
    refresh_token = "TOKEN-FALSE"
    response = ExtendedRequest().make_post(
        url=f"{ROUTE}/refresh-token",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 401
    assert response.json() == TOKEN_NOT_VALID

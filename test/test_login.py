import pytest
import requests

BASE_URL = "http://localhost:5000/login"  # Adjust the endpoint as needed

@pytest.mark.parametrize("email, password, expected_status, expected_message", [
    ("email@example.com", "password", 200, "Login successful"),
    ("email@example.com", "WrongPass123", 401, "Incorrect password. Please try again."),
    ("unknownuser@example.com", "RandomPass", 401, "Email not found. Please check your email and try again."),
])
def test_login(email, password, expected_status, expected_message):
    response = requests.post(BASE_URL, json={"email": email, "password": password})
    assert response.status_code == expected_status
    assert expected_message in response.json().get("message", "")

def test_session_persistence():
    email, password = "sessionuser@example.com", "ValidSessionPass"
    response = requests.post(BASE_URL, json={"email": email, "password": password})
    session_cookie = response.cookies.get("session")
    assert session_cookie is not None

def test_logout():
    email, password = "logoutuser@example.com", "LogoutPass123"
    login_response = requests.post(BASE_URL, json={"email": email, "password": password})
    session_cookie = login_response.cookies.get("session")
    
    # Logout
    response = requests.get(f"{BASE_URL}/logout", cookies={"session": session_cookie})
    assert response.status_code == 200
    assert response.json().get("message") == "Logged out successfully"

def test_login_empty_credentials():
    response = requests.post(BASE_URL, json={})
    assert response.status_code == 400
    assert "error" in response.json()  # Adjust based on your API response

def test_login_missing_email():
    response = requests.post(BASE_URL, json={"password": "password"})
    assert response.status_code == 400
    assert "error" in response.json()  # Adjust based on your API response

def test_login_missing_password():
    response = requests.post(BASE_URL, json={"email": "email@example.com"})
    assert response.status_code == 400
    assert "error" in response.json()  # Adjust based on your API response

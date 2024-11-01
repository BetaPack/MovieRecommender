import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.mark.parametrize("email, password, expected_status, expected_message", [
    ("email@example.com","password", 200, "Login successful"),
    ("validuser@example.com", "WrongPass123", 401, "Invalid credentials"),
    ("unknownuser@example.com", "RandomPass", 401, "Invalid credentials"),
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

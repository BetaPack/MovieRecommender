import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.mark.parametrize("email, password, expected_status, expected_message", [
    ("newuser@example.com", "StrongPass123", 200, "Account created successfully! Please login."),
    ("newuser@example.com", "StrongPass123", 200, "Account created successfully! Please login."),
    ("existinguser@example.com", "AnotherPass123", 401, "User with email already exists"),
    ("invalidemail.com", "ValidPass123", 400, "Invalid email format"),
    ("weakuser@example.com", "1234", 400, "Password too weak"),
])
def test_signup(email, password, expected_status, expected_message):
    # Send OTP first
    otp_response = requests.post(f"{BASE_URL}/send_otp", json={"email": email})
    assert otp_response.status_code == 200  # Ensure OTP is sent successfully

    # Attempt signup
    response = requests.post(f"{BASE_URL}/create-account", json={"email": email, "password": password})
    assert response.status_code == expected_status
    assert expected_message in response.json().get("message", "")

def test_resend_otp():
    email = "resendotp@example.com"
    response = requests.post(f"{BASE_URL}/send_otp", json={"email": email})
    assert response.status_code == 200
    assert "OTP sent to your email!" in response.json().get("message", "")

def test_otp_expiry():
    email = "expireotp@example.com"
    requests.post(f"{BASE_URL}/send_otp", json={"email": email})
    # Simulate expiry and retry
    response = requests.post(f"{BASE_URL}/send_otp", json={"email": email})
    assert response.status_code == 200
    assert "OTP sent to your email!" in response.json().get("message", "")

def test_invalid_otp():
    email = "invalidotp@example.com"
    requests.post(f"{BASE_URL}/send_otp", json={"email": email})
    response = requests.post(f"{BASE_URL}/verify-otp", json={"email": email, "otp": "000000"})
    assert response.status_code == 401
    assert "Invalid OTP" in response.json().get("message", "")

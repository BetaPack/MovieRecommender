import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.mark.parametrize("movie_list, expected_status", [
    (["Day of the Doctor, The (2013)"], 200),
    (["Wolf of Wall Street, The (2013)", "Wolf of Wall Street, The (2013)"], 200),
    (["Wolf of Wall Street, The (2013)", "Matrix, The (1999)"], 200),
    (["Inception (2010)", "Matrix, The (1999)", "Interstellar (2014)"], 200),
    ([], 400),
])
def test_predict(movie_list, expected_status):
    response = requests.post(f"{BASE_URL}/predict", json={"movie_list": movie_list})
    assert response.status_code == expected_status

def test_prediction_response_format():
    movie_list = ["Inception", "The Matrix", "Interstellar"]
    response = requests.post(f"{BASE_URL}/predict", json={"movie_list": movie_list})
    assert response.status_code == 200
    
    recommendations = response.json().get("recommendations", [])
    assert isinstance(recommendations, list)
    assert all("Title" in rec and "imdbRating" in rec for rec in recommendations)

def test_youtube_trailer_url():
    movie_list = ["Inception"]
    response = requests.post(f"{BASE_URL}/predict", json={"movie_list": movie_list})
    assert response.status_code == 200
    
    recommendations = response.json().get("recommendations", [])
    for rec in recommendations:
        trailer_url = rec.get("Trailer", "#")
        assert trailer_url.startswith("https://www.youtube.com/") or trailer_url == "#"

def test_predict_invalid_movie_name():
    movie_list = ["Nonexistent Movie (2022)"]
    response = requests.post(f"{BASE_URL}/predict", json={"movie_list": movie_list})
    assert response.status_code == 400
    assert "error" in response.json()  # Assuming the API returns an error message

def test_predict_empty_request():
    response = requests.post(f"{BASE_URL}/predict", json={})
    assert response.status_code == 400
    assert "error" in response.json()  # Assuming the API returns an error message


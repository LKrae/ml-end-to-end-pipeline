def test_predict_single(api_client, single_payload):
    response = api_client.post("/predict", json=single_payload)
    assert response.status_code == 200
    body = response.json()
    assert "prediction" in body
    assert isinstance(body["prediction"], (float, int))

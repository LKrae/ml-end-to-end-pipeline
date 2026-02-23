def test_predict_batch(api_client, batch_payload):
    response = api_client.post("/predict/batch", json=batch_payload)
    assert response.status_code == 200
    body = response.json()
    assert "predictions" in body
    assert len(body["predictions"]) == 2

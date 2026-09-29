def test_docs_page_uses_light_pink_background(client):
    response = client.get("/docs")

    assert response.status_code == 200
    assert "background-color: #fff0f5" in response.text
    assert "SwaggerUIBundle" in response.text


def test_openapi_schema_remains_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Basic Banking API"
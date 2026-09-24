from sentinelapi.openapi import parse_document


def test_openapi_paths_and_parameters_are_extracted():
    result = parse_document({
        "openapi": "3.0.0",
        "info": {"title": "fixture"},
        "paths": {"/users/{id}": {"get": {"parameters": [{"name": "id", "in": "path"}], "responses": {"200": {}}}}},
    }, "http://localhost/openapi.json")
    assert result["version"] == "3.0.0"
    assert result["endpoints"][0]["path"] == "/users/{id}"
    assert result["endpoints"][0]["parameters"][0]["name"] == "id"

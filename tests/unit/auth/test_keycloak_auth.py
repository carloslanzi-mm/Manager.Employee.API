import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, g
from flambda_app.auth.keycloak_auth import require_token
from keycloak.exceptions import KeycloakAuthenticationError


@pytest.fixture
def app():
    app = Flask(__name__)
    app.testing = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def build_mock_app_context(mock_keycloak, mock_logger):
    mock_app = MagicMock()
    mock_app.keycloak_openid = mock_keycloak
    mock_app.logger = mock_logger
    return mock_app


def test_missing_authorization_header(app):
    @app.route("/test")
    @require_token()
    def test_route():
        return jsonify({"message": "OK"})

    with app.test_request_context("/test"):
        response = test_route()
        assert response[1] == 401
        assert response[0].json["message"] == "Missing Authorization Token"


def test_inactive_token(app):
    mock_keycloak = MagicMock()
    mock_keycloak.introspect.return_value = {"active": False}
    mock_logger = MagicMock()

    @app.route("/test")
    @require_token()
    def test_route():
        return jsonify({"message": "OK"})

    with app.app_context():
        with app.test_request_context(
            "/test", headers={"Authorization": "Bearer fake_token"}
        ):
            with patch(
                "flambda_app.auth.keycloak_auth.current_app",
                build_mock_app_context(mock_keycloak, mock_logger),
            ):
                response = test_route()
                assert response[1] == 403
                assert response[0].json["message"] == "Token is inactive or expired"
                mock_logger.warning.assert_called_with("Token inativo ou expirado.")


def test_insufficient_roles(app):
    mock_keycloak = MagicMock()
    mock_keycloak.introspect.return_value = {
        "active": True,
        "realm_access": {"roles": ["user"]},
    }
    mock_logger = MagicMock()

    @app.route("/test")
    @require_token(required_roles=["admin"])
    def test_route():
        return jsonify({"message": "OK"})

    with app.app_context():
        with app.test_request_context(
            "/test", headers={"Authorization": "Bearer token"}
        ):
            with patch(
                "flambda_app.auth.keycloak_auth.current_app",
                build_mock_app_context(mock_keycloak, mock_logger),
            ):
                response = test_route()
                assert response[1] == 403
                assert response[0].json["message"] == "Insufficient permissions"
                mock_logger.warning.assert_called_with(
                    "Token sem permissões suficientes."
                )


def test_valid_token_and_roles(app):
    mock_keycloak = MagicMock()
    mock_keycloak.introspect.return_value = {
        "active": True,
        "realm_access": {"roles": ["admin"]},
        "preferred_username": "gilvan",
    }
    mock_logger = MagicMock()

    @app.route("/test")
    @require_token(required_roles=["admin"])
    def test_route():
        return jsonify({"message": "OK"})

    with app.app_context():
        with app.test_request_context(
            "/test", headers={"Authorization": "Bearer valid_token"}
        ):
            with patch(
                "flambda_app.auth.keycloak_auth.current_app",
                build_mock_app_context(mock_keycloak, mock_logger),
            ):
                response = test_route()
                assert response.status_code == 200
                assert response.json["message"] == "OK"


def test_keycloak_authentication_error(app):
    mock_keycloak = MagicMock()
    mock_keycloak.introspect.side_effect = KeycloakAuthenticationError("Auth error")
    mock_logger = MagicMock()

    @app.route("/test")
    @require_token()
    def test_route():
        return jsonify({"message": "OK"})

    with app.app_context():
        with app.test_request_context(
            "/test", headers={"Authorization": "Bearer token"}
        ):
            with patch(
                "flambda_app.auth.keycloak_auth.current_app",
                build_mock_app_context(mock_keycloak, mock_logger),
            ):
                response = test_route()
                assert response[1] == 403
                assert (
                    response[0].json["message"] == "Authentication with Keycloak failed"
                )
                mock_logger.error.assert_called()

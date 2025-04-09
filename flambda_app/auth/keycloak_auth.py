from functools import wraps
from flask import request, jsonify, current_app
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError

from flambda_app import config


CONFIG = config.get_config()

keycloak_openid = KeycloakOpenID(
    server_url=CONFIG.get("SERVER_KC", None),
    client_id=CONFIG.get("CLIENT_ID_KC", None),
    realm_name=CONFIG.get("REALM_NAME_KC", None),
    client_secret_key=CONFIG.get("CLIENT_SECRET_KC", None),
)


def require_token(required_roles=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            if not token:
                current_app.logger.warning("Token ausente no header Authorization.")
                return jsonify({"message": "Missing Authorization Token"}), 401

            try:
                introspection = current_app.keycloak_openid.introspect(token)
                if not introspection.get("active"):
                    current_app.logger.warning("Token inativo ou expirado.")
                    return jsonify({"message": "Token is inactive or expired"}), 403

                if required_roles:
                    token_roles = introspection.get("realm_access", {}).get("roles", [])
                    if not any(role in token_roles for role in required_roles):
                        current_app.logger.warning("Token sem permissões suficientes.")
                        return jsonify({"message": "Insufficient permissions"}), 403

                request.token_info = introspection

            except KeycloakAuthenticationError as e:
                current_app.logger.error(f"Erro de autenticação no Keycloak: {e}")
                return jsonify({"message": "Authentication with Keycloak failed"}), 403

            except Exception as e:
                current_app.logger.error(f"Erro ao validar token: {e}", exc_info=True)
                return jsonify({"message": "Token validation error"}), 500

            return f(*args, **kwargs)

        return decorated

    return wrapper

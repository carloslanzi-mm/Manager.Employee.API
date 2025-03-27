from flambda_app.connections.base_connection import BaseConnection
from flambda_app.schemas.turnstile import EmployeeTurnstileInputVO


class TurnstileConnection(BaseConnection):
    def __init__(self):
        super().__init__(
            base_url_env="TURNSTILE_API_URL", fallback_url="http://localhost:5000"
        )

    def create_employee_turnstile(self, input_vo: EmployeeTurnstileInputVO):
        response = self.session.post(
            self._url("/v1/turnstile"), json=input_vo.to_dict(), headers=self._headers()
        )
        self._handle_response(response, "criar")

    def update_employee_turnstile(self, input_vo: EmployeeTurnstileInputVO):
        uuid = input_vo.to_dict().get("uuid")
        response = self.session.put(
            self._url(f"/v1/turnstile/{uuid}"),
            json=input_vo.to_dict(),
            headers=self._headers(),
        )
        self._handle_response(response, "atualizar")

    def patch_employee_turnstile(self, input_vo: EmployeeTurnstileInputVO):
        data = input_vo.to_dict()
        uuid = data.get("uuid")
        patch_data = {"name": data.get("name"), "is_active": data.get("is_active")}
        response = self.session.patch(
            self._url(f"/v1/turnstile/{uuid}"), json=patch_data, headers=self._headers()
        )
        self._handle_response(response, "patch")

    def delete_employee_turnstile(self, uuid: str):
        response = self.session.delete(
            self._url(f"/v1/turnstile/{uuid}"), headers=self._headers()
        )
        self._handle_response(response, "deletar")

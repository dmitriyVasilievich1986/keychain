from flask_appbuilder.api import BaseApi, expose

from keychain import __version__ as app_version
from keychain.api.common.schemas import HealthResponse, VersionResponse


class CommonApi(BaseApi):
    resource_name = "health"
    route_base = ""

    @expose("/health", methods=["GET"])
    def health(self) -> dict[str, str]:
        """Returns the health status of the service.

        This endpoint can be used for health checks to verify that the service is running.
        It returns a serialized response indicating the status.

        Returns:
            dict: A dictionary containing the health status, e.g., {"status": "ok"}.

        """
        return HealthResponse().dump({"status": "ok"})

    @expose("/version", methods=["GET"])
    def version(self) -> dict[str, str]:
        """Returns the current application version.

        This method creates a VersionResponse object and serializes a dictionary containing
        the application's version information.

        Returns:
            dict: A serialized dictionary with the application's version.

        """
        return VersionResponse().dump({"version": app_version})

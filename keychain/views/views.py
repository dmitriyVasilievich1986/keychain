from __future__ import annotations

from flask_appbuilder import BaseView, expose
from flask_appbuilder.security.decorators import has_access


class PasswordView(BaseView):
    default_view = "pasword_view"
    route_base = "/password"

    @expose("/")
    @expose("/<string:pk>/")
    @has_access
    def pasword_view(
        self, pk: str | int | None = None  # pylint: disable=unused-argument
    ) -> str:
        """
        Renders the index.html template with the given appbuilder object.

        Args:
            pk (str | int | None): The primary key of the password (optional).

        Returns:
            str: The rendered template as a string.
        """

        return self.render_template("index.html", appbuilder=self.appbuilder)

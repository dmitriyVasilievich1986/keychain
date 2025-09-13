from typing import override

from flask_appbuilder import BaseView, expose, IndexView
from flask_appbuilder.security.decorators import has_access


class KeychainIndexView(IndexView):
    index_template = "index.html"

    @expose("/")
    @override
    @has_access
    def index(self) -> str:
        """
        Renders the index page of the views module.

        Returns:
            str: The rendered template of the index page.
        """

        self.update_redirect()
        return self.render_template(self.index_template, appbuilder=self.appbuilder)


class PasswordView(BaseView):
    default_view = "pasword_view"
    route_base = "/password"

    @expose("/")
    @expose("/<string:pk>/")
    @has_access
    def pasword_view(
        self,
        pk: str | int | None = None,  # pylint: disable=unused-argument
    ) -> str:
        """
        Renders the index.html template with the given appbuilder object.

        Args:
            pk (str | int | None): The primary key of the password (optional).

        Returns:
            str: The rendered template as a string.
        """

        return self.render_template("index.html", appbuilder=self.appbuilder)

from logging import getLogger

from flask_appbuilder._compat import as_unicode
from flask_appbuilder.const import LOGMSG_WAR_DBI_EDIT_INTEGRITY
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy.exc import IntegrityError

from keychain.models import Field

logger = getLogger(__name__)


class FieldSQLAInterface(SQLAInterface):
    def add_and_edit(
        self,
        *,
        to_edit: Field,
        raise_exception: bool = False,
        to_add: Field | None = None,
    ) -> bool:
        """
        Add and edit a field in the database.

        Args:
            to_edit (Field): The field to edit.
            raise_exception (bool, optional): Whether to raise an exception
                if an IntegrityError occurs. Defaults to False.
            to_add (Optional[Field], optional): The field to add.
                Defaults to None.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """

        try:
            if to_add is not None:
                self.session.add(to_add)
            self.session.merge(to_edit)
            self.session.commit()
            self.message = (as_unicode(self.edit_row_message), "success")
            return True
        except IntegrityError as e:
            self.message = (as_unicode(self.edit_integrity_error_message), "warning")
            logger.warning(LOGMSG_WAR_DBI_EDIT_INTEGRITY, e)
            self.session.rollback()
            if raise_exception:
                raise e
            return False
        except Exception as e:  # pylint: disable=broad-except
            self.message = (as_unicode(self.database_error_message), "danger")
            logger.exception("Database error")
            self.session.rollback()
            if raise_exception:
                raise e
            return False

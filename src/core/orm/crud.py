"""Core ORM module."""

from src.core.orm.cruds.auth import AuthUsers
from src.core.orm.cruds.refer import Refer
from src.core.orm.cruds.user import Users


class Crud:
    """Interface for combined CRUD operations.

    Attributes:
        users (Users): CRUD for user model.
        auth (AuthUsers): CRUD for authentication model.
        refer (Refer): CRUD for referral model.
    """

    def __init__(
        self,
        user_crud: Users,
        auth_crud: AuthUsers,
        refer: Refer,
    ) -> None:
        """
        Initialize Crud with CRUD instances.

        Args:
            user_crud (Users): User model CRUD instance.
            auth_crud (AuthUsers): Auth model CRUD instance.
            refer (Refer): Referral model CRUD instance.
        """
        self.users = user_crud
        self.auth = auth_crud
        self.refer = refer


def create_crud_helper() -> Crud:
    """Initialize and return a Crud instance with models.

    Returns:
        Crud: Initialized Crud instance.
    """
    return Crud(
        user_crud=Users(),
        auth_crud=AuthUsers(),
        refer=Refer(),
    )

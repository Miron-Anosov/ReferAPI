"""User model validator."""

import pydantic


class User(pydantic.BaseModel):
    """**Model for tweet author details**.

     - `id`: str: Identification of user.
    - `name`: User's name.
    """

    id: str = pydantic.Field(
        description="Identification of user.",
    )
    name: str = pydantic.Field(
        ...,
        description="User's name.",
        min_length=2,
        max_length=15,
    )

    model_config = pydantic.ConfigDict(title="User")


class UserReferrals(pydantic.BaseModel):
    """Validate model for profile of user."""

    id: str
    name: str
    referrals: list[User | None]

    model_config = pydantic.ConfigDict(title="User's referrals")

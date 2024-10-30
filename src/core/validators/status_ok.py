"""Validator models for all successful responses or unsuccessful."""

import pydantic


class Status(pydantic.BaseModel):
    """**Movel validate response status  /tweets /users**.

    - `result`: bool : Successful or unsuccessful.

    """

    result: bool = True
    model_config = pydantic.ConfigDict(title="Status OK")

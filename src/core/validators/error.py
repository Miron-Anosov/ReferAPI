"""Error Response to clients."""

import pydantic


class ErrorMessage(pydantic.BaseModel):
    """Response error.

    If Api will have any errors, it will send to client.
    Args:
        result (bool): default False
        error_type (str): description error
        error_message (str): message error
    """

    result: bool = False
    error_type: str
    error_message: str

    model_config = pydantic.ConfigDict(title="Error")

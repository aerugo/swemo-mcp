from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    """
    Shared argument object for every *forecast* tool.
    """

    policy_round: str | None = Field(
        None, pattern=r"^(\d{4}:\d|latest)$", description="E.g. '2024:3' or 'latest'.  None ⇒ all vintages."
    )
    include_realized: bool = False

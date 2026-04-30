from pydantic import BaseModel, ConfigDict


class CustomModel(BaseModel):
    """Base schema for all Pydantic models in this project.

    Enables ORM mode so SQLAlchemy row objects can be passed directly.
    Use timezone-aware datetimes in all fields — asyncpg returns UTC by default.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

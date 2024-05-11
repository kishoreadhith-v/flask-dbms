from bson import ObjectId
from pydantic.json import ENCODERS_BY_TYPE

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(
            type='string',
            examples = ['663e447073484f58fe1158c8', '663e4b337f652c8dc48ec6a1'],
        )

ENCODERS_BY_TYPE[ObjectId] = str
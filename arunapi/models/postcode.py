from postcode_validator.Exceptions.exceptions import ValidationError
from postcode_validator.uk.uk_postcode_validator import UKPostcode


class PostCode(str, UKPostcode):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(examples=["BN17 5LF", "bn175lf"])

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError("string required")
        try:
            m = UKPostcode(value)
        except ValidationError as e:
            raise ValueError(str(e))
        return m

    def __repr__(self) -> str:
        return self.postcode

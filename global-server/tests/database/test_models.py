from datetime import date
import pytest

from src.database import models
from src.database import types_


class TestValidations:

    def test_default_actor_name_in_capitals(self):
        with pytest.raises(ValueError):
            models.DefaultActor(actor_id=3, name="lowercase")

    def test_user_invalid_phone(self, password: str):
        with pytest.raises(types_.exceptions.PhoneValidationError):
            models.User(
                hashed_password=password,
                actor_id=1,
                role=types_.enums.UserRole.customer,
                email="example@gmail.com",
                phone=1876543210,
                fname="Иван",
                birth_date=date(year=2000, day=1, month=1),
            )

    def test_user_invalid_email(self, password: str):
        with pytest.raises(types_.exceptions.EmailValidationError):
            models.User(
                hashed_password=password,
                actor_id=1,
                role=types_.enums.UserRole.customer,
                email="foo",
                phone=9876543210,
                fname="Иван",
                birth_date=date(year=2000, day=1, month=1),
            )

    def test_user_password_unhashed(self):
        with pytest.raises(types_.exceptions.PasswordValidationError):
            models.User(
                hashed_password="foo",
                actor_id=1,
                role=types_.enums.UserRole.customer,
                email="example@gmail.com",
                phone=9876543210,
                fname="Иван",
                birth_date=date(year=2000, day=1, month=1),
            )

    def test_user_age_low(self, password: str):
        with pytest.raises(types_.exceptions.BirthDateValidationError):
            models.User(
                hashed_password=password,
                actor_id=1,
                role=types_.enums.UserRole.customer,
                email="example@gmail.com",
                phone=9876543210,
                fname="Иван",
                birth_date=date.today()
            )

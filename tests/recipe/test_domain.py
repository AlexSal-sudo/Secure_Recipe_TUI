from recipe.domain import User, Recipe, Description, Title, Name, Quantity, Unit
import pytest
from valid8 import ValidationError


def test_new_user():
    wrong_values = ['new username', 'new_username', 'newusername' * 20]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            User(value)

    correct_values = ['newUsername', 'newusername', 'newUsername10']
    for value in correct_values:
        assert User(value).username == value


def test_new_recipe():
    pass


# devo effettivamente scrivere un test per le recipe?


def test_new_name():
    wrong_values = ['new name', 'new_name', 'newname' * 20]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Name(value)

    correct_values = ['NewName', 'newName', 'newname']
    for value in correct_values:
        assert Name(value).value == value


def test_new_quantity():
    wrong_values = [0, 00]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Quantity(value)

    correct_values = [10, 1, 1000]
    for value in correct_values:
        assert Quantity(value).value == value


def test_new_unit():
    wrong_values = ['kilograms', 'liters', 'grams']
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Unit(value)

    correct_values = ['kg', 'g', 'n/a']
    for value in correct_values:
        assert Unit(value).value == value


def test_new_description():
    wrong_values = ['This is a new description!', 'This is a new description 123',
                    'This is a new description-' * 200]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Description(value)

    correct_values = ['This is a new description.', 'This is a new description, bye.',
                      'This is a new description; goodbye.']
    for value in correct_values:
        assert Description(value).value == value


def test_new_title():
    wrong_values = ['This is a new title!', 'This is a new title 123',
                    'This is a new tile' * 30]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Title(value)

    correct_values = ['This is a new title', 'This is a new new title',
                      'This is a new new new title']
    for value in correct_values:
        assert Title(value).value == value

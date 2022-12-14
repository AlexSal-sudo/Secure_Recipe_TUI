from datetime import date
from unittest import mock
from unittest.mock import patch

from recipe.domain import Recipe, Description, Title, Name, Quantity, Unit, Ingredient, Password, Username, Email, Id
from recipe.domain import JsonHandler
import pytest
from valid8 import ValidationError


def test_new_name():
    wrong_values = ['new!name', 'new_name', 'newname' * 20]
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
    wrong_values = ['kilograms', 'liters', 'grams', 'teaspoon']
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Unit(value)

    correct_values = ['kg', 'g', 'n/a', 'cup']
    for value in correct_values:
        assert Unit(value).value == value


def test_new_description():
    wrong_values = ['This is a new description_', 'This is a new description?',
                    'This is a new description-' * 400]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Description(value)

    correct_values = ['This is a new description.', 'This is a new description123, bye.',
                      'This is a new description; goodbye.\n']
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


def test_new_recipe():
    with pytest.raises(TypeError):
        Recipe.Builder(1, 'title', 123, 'description1', date.today(),
                       date.today()).with_ingredient(Ingredient('name', 10, 'n/a')).build()
    with pytest.raises(TypeError):
        Recipe.Builder(Id(1), Title('title'), Username('username'), Description('description1'), date.today(),
                       date.today()).with_ingredient(Ingredient('name', 10, 'n/a')).build()
    new_recipe = Recipe.Builder(Id(1), Title('title'), Username('username'), Description('description1'), date.today(),
                                date.today()).with_ingredient(Ingredient(Name('name'), Quantity(10),
                                                                         Unit('n/a'))).build()
    assert new_recipe.title.value == 'title'
    assert new_recipe.author.value == 'username'
    assert new_recipe.description.value == 'description1'
    assert new_recipe.created_at == date.today()
    assert new_recipe.updated_at == date.today()


@pytest.mark.parametrize('name, quantity, unit', [
    ('water', 1, 'l'),
    ('water', 10, 'kg')
])
def test_new_right_ingredient(name, quantity, unit):
    new_ingredient = Ingredient(Name(name), Quantity(quantity), Unit(unit))
    assert new_ingredient.name.value == name
    assert new_ingredient.quantity.value == quantity
    assert new_ingredient.unit.value == unit


@pytest.mark.parametrize('name, quantity, unit', [
    ('water', 0, 'l'),
    ('water', 10, 'kilograms')
])
def test_new_wrong_ingredient(name, quantity, unit):
    with pytest.raises(ValidationError):
        Ingredient(Name(name), Quantity(quantity), Unit(unit))


def test_json_converter_ingredients():
    my_right_json_ingredient = {
        'name': 'water',
        'quantity': 1,
        'unit': 'l'
    }
    my_wrong_json_ingredient = {
        'name': 'water',
        'quantity': '1',
        'unit': 'l'
    }

    with pytest.raises(TypeError):
        JsonHandler.create_ingredients_from_json(my_wrong_json_ingredient)

    new_ingredient = JsonHandler.create_ingredients_from_json(my_right_json_ingredient)
    assert new_ingredient.unit.value == 'l'
    assert new_ingredient.quantity.value == 1
    assert new_ingredient.name.value == 'water'


def test_json_converter_recipe():
    my_right_json_recipe = {
        'id': 1,
        'author': 'author',
        'title': 'title',
        'description': 'description1',
        'ingredients': [{
            'name': 'ingredient',
            'quantity': 1,
            'unit': 'n/a'
        }],
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    }
    new_recipe = JsonHandler.create_recipe_from_json(my_right_json_recipe)
    assert new_recipe.title.value == 'title'
    assert new_recipe.description.value == 'description1'

    my_wrong_json_recipe = {
        'description': 'description1',
        'ingredients': [{
            'name': 'ingredient',
            'quantity': 1,
            'unit': 'n/a'
        }],
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    }
    with pytest.raises(KeyError):
        JsonHandler.create_recipe_from_json(my_wrong_json_recipe)


def test_password():
    wrong_values = ['This is a password', 'pass',
                    'This is a password' * 50]
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Password(value)

    correct_values = ['This_is_a_password', 'new_pass',
                      'password@1234']
    for value in correct_values:
        assert Password(value).value == value


def test_username():
    wrong_values = ['This is an username', 'new!username',
                    'us']
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Username(value)

    correct_values = ['This_is_an_username', 'newUsername',
                      'username234']
    for value in correct_values:
        assert Username(value).value == value


def test_email():
    wrong_values = ['secure recipe', 'secure recipe@gmail',
                    'secure.recipe.it']
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Email(value)

    correct_values = ['secure.recipe@gmail.com', 'secure00recipe@icloud.com',
                      'secure.recipe00@libero.it']
    for value in correct_values:
        assert Email(value).value == value


@patch('builtins.print')
def test_print_recipe(mock_print):
    new_recipe = Recipe.Builder(Id(1), Title('title'), Username('username'), Description('description1'), date.today(),
                                date.today()).with_ingredient(Ingredient(Name('name'), Quantity(10),
                                                                         Unit('n/a'))).build()
    new_recipe.print()
    mock_print.assert_any_call('title')
    mock_print.assert_any_call('Description: description1')
    mock_print.assert_any_call('Author: username')

import datetime

from recipe.domain import User, Recipe, Description, Title, Name, Quantity, Unit, Ingredient
from recipe.domain import JsonHandler
import pytest
from valid8 import ValidationError


def test_new_user():
    wrong_values = 'abc'
    with pytest.raises(TypeError):
        User(wrong_values)

    wrong_values = -1
    with pytest.raises(ValidationError):
        User(wrong_values)

    correct_values = [1, 12, 123]
    for value in correct_values:
        assert User(value).id == value


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
    wrong_values = ['kilograms', 'liters', 'grams', 'teaspoon']
    for value in wrong_values:
        with pytest.raises(ValidationError):
            Unit(value)

    correct_values = ['kg', 'g', 'n/a', 'cup']
    for value in correct_values:
        assert Unit(value).value == value


def test_new_description():
    wrong_values = ['This is a new description!', 'This is a new description?',
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
        Recipe.Builder('title', 123, 'description1', datetime.datetime.now(),
                       datetime.datetime.now()).with_ingredient(Ingredient('name', 10, 'n/a')).build()
    with pytest.raises(TypeError):
        Recipe.Builder(Title('title'), User(123), Description('description1'), datetime.datetime.now(),
                       datetime.datetime.now()).with_ingredient(Ingredient('name', 10, 'n/a')).build()
    new_recipe = Recipe.Builder(Title('title'), User(123), Description('description1'), datetime.datetime.now(),
                                datetime.datetime.now()).with_ingredient(Ingredient(Name('name'), Quantity(10),
                                                                                    Unit('n/a'))).build()
    assert new_recipe.recipe_title.value == 'title'
    assert new_recipe.recipe_author.id == 123
    assert new_recipe.recipe_description.value == 'description1'


@pytest.mark.parametrize('name, quantity, unit', [
    ('water', 1, 'l'),
    ('water', 10, 'kg')
])
def test_new_right_ingredient(name, quantity, unit):
    new_ingredient = Ingredient(Name(name), Quantity(quantity), Unit(unit))
    assert new_ingredient.ingredient_name.value == name
    assert new_ingredient.ingredient_quantity.value == quantity
    assert new_ingredient.ingredient_unit.value == unit


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
    assert new_ingredient.ingredient_unit.value == 'l'
    assert new_ingredient.ingredient_quantity.value == 1
    assert new_ingredient.ingredient_name.value == 'water'


def test_json_converter_recipe():
    my_right_json_recipe = {
        'id': 1,
        'author': 1,
        'title': 'title',
        'description': 'description1',
        'ingredients': [{
            'name': 'ingredient',
            'quantity': 1,
            'unit': 'n/a'
        }],
        'created_at': '2022-12-01T15:15:12.376396Z',
        'updated_at': '2022-12-01T15:15:12.376396Z',
    }
    new_recipe = JsonHandler.create_recipe_from_json(my_right_json_recipe)
    assert new_recipe.recipe_title.value == 'title'
    assert new_recipe.recipe_description.value == 'description1'

    my_wrong_json_recipe = {
        'description': 'description1',
        'ingredients': [{
            'name': 'ingredient',
            'quantity': 1,
            'unit': 'n/a'
        }],
        'created_at': '2022-12-01T15:15:12.376396Z',
        'updated_at': '2022-12-01T15:15:12.376396Z',
    }
    with pytest.raises(KeyError):
        JsonHandler.create_recipe_from_json(my_wrong_json_recipe)

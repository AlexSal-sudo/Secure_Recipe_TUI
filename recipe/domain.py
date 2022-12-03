from dataclasses import dataclass, InitVar, field
from typing import Any, Optional, List, Dict

import requests
from typeguard import typechecked
from valid8 import validate
from validation.regex import pattern

import datetime


@typechecked
@dataclass(frozen=True, order=True)
class Title:
    value: str

    def __post_init__(self):
        validate('title', self.value, min_len=1, max_len=30, custom=pattern(r'[a-zA-Z ]+'))


@typechecked
@dataclass(frozen=True)
class User:
    id: int

    def __post_init__(self):
        validate('username', self.id, min_value=0)


@typechecked
@dataclass(frozen=True, order=True)
class Description:
    value: str

    def __post_init__(self):
        validate('title', self.value, min_len=1, max_len=500, custom=pattern(r'[a-zA-Z0-9 \n.,;]+'))


@typechecked
@dataclass(frozen=True, order=True)
class Name:
    value: str

    def __post_init__(self):
        validate('name', self.value, min_len=1, max_len=30, custom=pattern(r'^[a-zA-Z]+$'))


@typechecked
@dataclass(frozen=True, order=True)
class Quantity:
    value: int

    def __post_init__(self):
        validate('quantity', self.value, min_value=1, max_value=1000)


@typechecked
@dataclass(frozen=True)
class Unit:
    value: str
    _my_units = ['kg', 'g', 'l', 'cl', 'ml', 'cup', 'n/a']

    def __post_init__(self):
        validate('value', self.value, min_len=1, max_len=3, custom=self._is_a_correct_unit)

    def _is_a_correct_unit(self, value) -> bool:
        return value in self._my_units


@typechecked
@dataclass(frozen=True)
class Ingredient:
    name: Name
    quantity: Quantity
    unit: Unit

    @property
    def ingredient_name(self):
        return self.name

    @property
    def ingredient_quantity(self):
        return self.quantity

    @property
    def ingredient_unit(self):
        return self.unit


@typechecked
@dataclass(frozen=True)
class Recipe:
    title: Title
    author: User
    description: Description
    created_at: datetime
    updated_at: datetime
    __ingredients: List[Ingredient] = field(default_factory=list, repr=False, init=False)
    __map_of_ingredients: Dict[Name, Ingredient] = field(default_factory=dict, repr=False, init=False)
    create_key: InitVar[Any] = field(default='None')

    def __post_init__(self, create_key: Any):
        validate('create_key', create_key, custom=Recipe.Builder.is_valid_key)

    def _add_ingredient(self, ingredient: Ingredient, create_key: Any) -> None:
        validate('create_key', create_key, custom=Recipe.Builder.is_valid_key)
        validate('ingredient.name', ingredient.name, custom=lambda v: v not in self.__map_of_ingredients)
        self.__ingredients.append(ingredient)
        self.__map_of_ingredients[ingredient.name] = ingredient

    def _has_at_least_one_ingredient(self):
        return len(self.__ingredients) >= 1

    @property
    def recipe_title(self):
        return self.title

    @property
    def recipe_author(self):
        return self.author

    @property
    def recipe_description(self):
        return self.description

    @typechecked
    @dataclass()
    class Builder:
        __recipe: Optional['Recipe']
        __create_key = object()

        def __init__(self, title: Title, author: User, description: Description, created_at: datetime,
                     updated_at: datetime):
            self.__recipe = Recipe(title, author, description, created_at, updated_at, self.__create_key)

        @staticmethod
        def is_valid_key(key: Any) -> bool:
            return key == Recipe.Builder.__create_key

        def with_ingredient(self, ingredient: Ingredient) -> 'Recipe.Builder':
            validate('recipe', self.__recipe)
            self.__recipe._add_ingredient(ingredient, self.__create_key)
            return self

        def build(self) -> 'Recipe':
            validate('recipe', self.__recipe)
            validate('recipe.ingredients', self.__recipe._has_at_least_one_ingredient(), equals=True)
            final_recipe, self.__recipe = self.__recipe, None
            return final_recipe


@typechecked
@dataclass(frozen=True)
class JsonHandler:
    @staticmethod
    def create_ingredients_from_json(ingredient) -> Ingredient:
        return Ingredient(Name(ingredient['name']), Quantity(ingredient['quantity']), Unit(ingredient['unit']))

    @staticmethod
    def create_recipe_from_json(json):
        new_recipe = Recipe.Builder(Title(json['title']), User(json['author']), Description(json['description']),
                                    json['created_at'], json['updated_at'])
        for ingredient in json['ingredients']:
            new_recipe.with_ingredient(JsonHandler.create_ingredients_from_json(ingredient))
        new_recipe = new_recipe.build()
        return new_recipe


@typechecked
@dataclass(frozen=True)
class DealerRecipes:
    __api_server = 'https://localhost:8000/api/v1'

    def login(self, username, password):
        res = requests.post(url=f'{self.__api_server}/auth/login',
                            data={'username': username, 'password': password})
        if res.status_code != 200:
            return None
        json = res.json()
        return json['key']

    def logout(self, key):
        res = requests.post(url=f'{self.__api_server}/auth/logout',
                            headers={'Authorization': f'Token {key}'})
        if res.status_code == 200:
            return 'Logged out!'
        else:
            return 'Logout failed!'

    def add_new_recipe(self, key, title, description, ingredients):
        res = requests.post(url=f'{self.__api_server}/recipes', headers={'Authorization': f'Token {key}'},
                            data={'title': title, 'description': description,
                                  'ingredients': ingredients})
        return res.json()

    def delete_recipe(self, key, index):
        res = requests.delete(url=f'{self.__api_server}/recipes/{index}', headers={'Authorization': f'Token {key}'},
                              data={'id': index})
        if res.status_code != 202:
            return 'Error during cancellation of the recipe.'
        else:
            return 'The recipe is cancelled!'

    def show_all_recipes(self, key):
        res = requests.get(url=f'{self.__api_server}/recipes',
                           headers={'Authorization': f'Token {key}'})
        if res.status_code != 200:
            return None
        return res.json()

    def show_specific_recipe(self, key, index):
        res = requests.get(url=f'{self.__api_server}/recipes/{index}',
                           headers={'Authorization': f'Token {key}'})
        if res.status_code != 200:
            return None
        return res.json()

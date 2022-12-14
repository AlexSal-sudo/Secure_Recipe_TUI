import json
from dataclasses import dataclass, InitVar, field
from typing import Any, Optional, List, Dict

import requests
from typeguard import typechecked
from valid8 import validate

from datetime import date, datetime
from validation.regex import pattern


# TODO
# inserire messaggi nel validate per spiegare cosa si sta rompendo


@typechecked
@dataclass(frozen=True, order=True)
class Title:
    value: str

    def __post_init__(self):
        validate('title', self.value, min_len=1, max_len=30, custom=pattern(r'^[a-zA-Z ]+$'))


@typechecked
@dataclass(frozen=True)
class Id:
    id: int

    def __post_init__(self):
        validate('id', self.id, min_value=0)


@typechecked
@dataclass(frozen=True, order=True)
class Username:
    value: str

    def __post_init__(self):
        validate('password', self.value, min_len=4, max_len=30, custom=pattern(r'^[a-zA-Z0-9_\-\.]+$'))


@typechecked
@dataclass(frozen=True, order=True)
class Description:
    value: str

    def __post_init__(self):
        validate('title', self.value, min_len=1, max_len=500, custom=pattern(r'^[a-zA-Z0-9À-ú \'!;\.,\n]+'))


@typechecked
@dataclass(frozen=True, order=True)
class Name:
    value: str

    def __post_init__(self):
        validate('name', self.value, min_len=1, max_len=30, custom=pattern(r'^[a-zA-ZÀ-ú ]+$'))


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


@typechecked
@dataclass(frozen=True)
class Recipe:
    id: Id
    title: Title
    author: Username
    description: Description
    created_at: date
    updated_at: Optional['date'] = field(default=None)
    __ingredients: List[Ingredient] = field(default_factory=list, repr=False, init=False)
    __map_of_ingredients: Dict[Name, Ingredient] = field(default_factory=dict, repr=False, init=False)
    create_key: InitVar[Any] = field(default='None')

    def print(self) -> None:
        print('-' * 50)
        print(self.title.value)
        print('-' * 50)
        print(f'Id: {self.id.id}')
        print(f'Description: {self.description.value}')
        print(f'Author: {self.author.value}')
        print(f'Created_at: {self.created_at.__str__()}')
        if self.updated_at is not None:
            print(f'Updated_at: {self.updated_at.__str__()}')
        print('Ingredients:')
        for ingredient in self.__ingredients:
            print(f'\t-{ingredient.name.value}: {ingredient.quantity.value} {ingredient.unit.value}')
        print('')

    def __post_init__(self, create_key: Any):
        validate('create_key', create_key, custom=Recipe.Builder.is_valid_key)

    def _add_ingredient(self, ingredient: Ingredient, create_key: Any) -> None:
        validate('create_key', create_key, custom=Recipe.Builder.is_valid_key)
        validate('ingredient.name', ingredient.name, custom=lambda v: v not in self.__map_of_ingredients)
        self.__ingredients.append(ingredient)
        self.__map_of_ingredients[ingredient.name] = ingredient

    def _has_at_least_one_ingredient(self):
        return len(self.__ingredients) >= 1

    @typechecked
    @dataclass()
    class Builder:
        __recipe: Optional['Recipe']
        __create_key = object()

        def __init__(self, id: Id, title: Title, author: Username, description: Description, created_at: date,
                     updated_at: date | None):
            self.__recipe = Recipe(id, title, author, description, created_at, updated_at, self.__create_key)

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
        update_field = None
        if 'updated_at' in json:
            update_field = datetime.strptime(json['updated_at'], '%Y-%m-%d').date()
        new_recipe = Recipe.Builder(Id(json['id']), Title(json['title']), Username(json['author']), Description(json['description']),
                                    datetime.strptime(json['created_at'], '%Y-%m-%d').date(), update_field)
        for ingredient in json['ingredients']:
            new_recipe = new_recipe.with_ingredient(JsonHandler.create_ingredients_from_json(ingredient))
        new_recipe = new_recipe.build()
        return new_recipe


@typechecked
@dataclass(frozen=True)
class DealerRecipes:
    __api_server = 'http://localhost:8000/api/v1'

    def sign_up(self, username, email, password, confirm_password):
        my_data = {
            'username': username,
            'email': email,
            'password1': password,
            'password2': confirm_password
        }
        res = requests.post(url=f'{self.__api_server}/auth/registration/', data=my_data)
        if res.status_code != 201:
            # TODO
            # come faccio a restituire direttamente il risultato del json? non so quale campo stampa,
            # così è più immediato
            return res.json()
        else:
            # TODO
            # restituisce la chiave ma non lo logga in automatico, lascio così ve?
            return 'Welcome to Secure Recipe! You are now registered as a new user.'

    def login(self, username, password):
        res = requests.post(url=f'{self.__api_server}/auth/login/', data={'username': username, 'password': password})
        if res.status_code != 200:
            return None
        json = res.json()
        return json['key']

    def logout(self, key):
        res = requests.post(url=f'{self.__api_server}/auth/logout/', headers={'Authorization': f'Token {key}'})
        if res.status_code == 200:
            return 'Logged out!'
        else:
            return 'Logout failed!'

    def add_new_recipe(self, key, title, description, ingredients):
        data = {
            'title': title,
            'description': description,
            'ingredients': ingredients
        }
        res = requests.post(url=f'{self.__api_server}/personal-area/', headers={'Authorization': f'Token {key}',
                                                                                'Content-Type': 'application/json'},
                            data=json.dumps(data))
        return res.json()

    def delete_recipe(self, key, index):
        res = requests.delete(url=f'{self.__api_server}/personal-area/{index}/',
                              headers={'Authorization': f'Token {key}'},
                              data={'id': index})
        if res.status_code != 204:
            return res.json()['detail']
        else:
            return 'The recipe is cancelled!'

    def show_all_recipes(self):
        return self.get_request(view=f'/recipes/')

    def show_specific_recipe(self, index):
        return self.get_request(view=f'/recipes/{index}/')

    def sort_by_title(self):
        return self.get_request(view='/recipes/sort-by-title/')

    def sort_by_date(self):
        return self.get_request(view='/recipes/sort-by-date/')

    def sort_my_recipes_by_title(self, key):
        return self.get_request(view='/personal-area/sort-by-title/', headers={'Authorization': f'Token {key}'})

    def sort_my_recipes_by_date(self, key):
        return self.get_request(view='/personal-area/sort-by-date/', headers={'Authorization': f'Token {key}'})

    def filter_by_author(self, author):
        return self.get_request(view=f'/recipes/by-author/{author}/')

    def filter_by_title(self, title):
        return self.get_request(view=f'/recipes/by-title/{title}/')

    def filter_by_ingredient(self, ingredient):
        return self.get_request(view=f'/recipes/by-ingredient/{ingredient}/')

    def what_is_my_role(self, key):
        result = self.get_request(view=f'/personal-area/account-type/', headers={'Authorization': f'Token {key}'})
        if 'detail' in result:
            return result['detail']
        else:
            if result['type-account'] == 0:
                return 'You are logged as normal user'
            elif result['type-account'] == 1:
                return 'You are logged as admin'
            else:
                return 'You are logged as moderator'

    def update_my_recipe(self, key, index, recipe_to_change):
        res = requests.put(url=f'{self.__api_server}/personal-area/{index}/',
                           headers={'Authorization': f'Token {key}', 'Content-Type': 'application/json'},
                           data=json.dumps(recipe_to_change))
        return res.json()

    def get_request(self, view, **kwargs):
        data = kwargs['data'] if 'data' in kwargs else {}
        headers = kwargs['headers'] if 'headers' in kwargs else {}
        res = requests.get(url=f'{self.__api_server}{view}', headers=headers, data=data)
        return res.json()


@typechecked
@dataclass(frozen=True, order=True)
class Password:
    value: str

    def __post_init__(self):
        validate('password', self.value, min_len=8, max_len=30, custom=pattern(r'^[a-zA-Z0-9_\-@#*\.!?$^=+]+$'))


@typechecked
@dataclass(frozen=True, order=True)
class Email:
    value: str

    def __post_init__(self):
        validate('email', self.value, min_len=8, max_len=30, custom=pattern(r'^[a-zA-Z0-9\.]+@[a-z]+\.[a-z]+$'))

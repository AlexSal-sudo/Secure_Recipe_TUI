from dataclasses import dataclass

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
    username: str

    def __post_init__(self):
        validate('username', self.username, min_len=3, max_len=20, custom=pattern(r'[a-zA-Z0-9]+'))


@typechecked
@dataclass(frozen=True, order=True)
class Description:
    value: str

    def __post_init__(self):
        validate('title', self.value, min_len=1, max_len=300, custom=pattern(r'[a-zA-Z \.,;]+'))


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

    def __post_init__(self):
        validate('value', self.value, min_len=1, max_len=3, custom=pattern(r'^(g|kg|l|n\/a)$'))


@typechecked
@dataclass(frozen=True)
class Ingredient:
    name: Name
    quantity: Quantity
    unit: Unit


@typechecked
@dataclass(frozen=True)
class Recipe:
    title: Title
    author: User
    description: Description
    created_at: datetime
    updated_at: datetime
    ingredients: Ingredient


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

    # posso inserire una nuova ricetta solo se sono autenticato
    def add_new_recipe(self, key, title, description, ingredients):
        res = requests.post(url=f'{self.__api_server}/recipes', headers={'Authorization': f'Token {key}'},
                            data={'title': title, 'description': description,
                                  'ingredients': ingredients})
        return res.json()

    # posso cancellare una ricetta solo se sono un super user
    def delete_recipe(self, key, index):
        res = requests.delete(url=f'{self.__api_server}/recipes/{index}', headers={'Authorization': f'Token {key}'},
                              data={'id': index})
        if res.status_code != 202:
            return 'Error during cancellation of the recipe.'
        else:
            return 'The recipe is cancelled!'

    # posso visualizzare tutte le ricette indipendentemente dal login
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

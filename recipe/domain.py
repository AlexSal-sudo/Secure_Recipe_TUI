from dataclasses import dataclass

import requests
from typeguard import typechecked
from typing import Dict, List
from valid8 import validate
from validation.regex import pattern

import datetime


@typechecked
@dataclass(frozen=True, order=True)
class Title:
    value: str

    def __post_init__(self):
        validate('title', self.value, min_len=1, max_len=30, custom=pattern(r'[a-zA-Z ]*'))


@typechecked
@dataclass(frozen=True)
class User:
    username: str

    def __post_init__(self):
        validate('username', self.username, min_len=3, max_len=20, custom=pattern(r'[a-zA-Z]*'))


@typechecked
@dataclass(frozen=True, order=True)
class Description:
    value: str

    def __post_init__(self):
        validate('title', self.value, min_len=1, max_len=300, custom=pattern(r'[a-zA-Z \.,;]*'))


@typechecked
@dataclass(frozen=True)
class Recipe:
    title: Title
    author: User
    description: Description
    created_at: datetime
    ingredients: Dict
    steps: List


@typechecked
@dataclass(frozen=True)
class DealerRecipes:
    __api_server = 'api/v1/'

    def __login(self, username, password):
        pass

    def __logout(self, key):
        pass

    def __add_new_recipe(self, key):
        pass

    def __delete_new_recipe(self, key):
        pass

    def __show_all_recipe(self, key):
        pass

    def __show_specific_recipe(self, key, index):
        pass

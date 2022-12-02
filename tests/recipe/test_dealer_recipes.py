import pytest
import requests_mock
from recipe.domain import DealerRecipes


@pytest.fixture
def data_for_login():
    data = [
        ('username1', 'password1'),
        ('username2', 'password2')
    ]
    return data


@pytest.fixture
def key_for_tests():
    data = ['key1', 'key3', 'my_fake_token']
    return data


def check_data_for_login_json(username, password, data_for_login):
    for data in data_for_login:
        if data[0] == username and data[1] == password:
            return {
                'key': 'fake_token_provided'
            }
        return {}


def check_data_for_login_status_code(username, password, data_for_login):
    for data in data_for_login:
        if data[0] == username and data[1] == password:
            return 200
        return 400


@pytest.mark.parametrize('username, password, result', [
    ('username1', 'password1', 'fake_token_provided'),
    ('username3', 'password3', None)
])
def test_login(username, password, result, data_for_login):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.post('https://localhost:8000/api/v1/auth/login',
               status_code=check_data_for_login_status_code(username, password, data_for_login),
               json=check_data_for_login_json(username, password, data_for_login))
        assert my_dealer.login(username, password) == result


@pytest.mark.parametrize('key, result', [
    ('key1', 'Logged out!'),
    ('key2', 'Logout failed!')
])
def test_logout(key, result, key_for_tests):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.post('https://localhost:8000/api/v1/auth/logout', status_code=200 if key in key_for_tests else 400)
        assert my_dealer.logout(key) == result


@pytest.mark.parametrize('key, index, status_code, result', [
    ('my_fake_token', 1, 400, 'Error during cancellation of the recipe.'),
    ('my_fake_token', 2, 202, 'The recipe is cancelled!')
])
def test_delete_recipe(key, index, status_code, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.delete(f'https://localhost:8000/api/v1/recipes/{index}', status_code=status_code)
        assert my_dealer.delete_recipe(key, index) == result


@pytest.mark.parametrize('key, my_result', [
    ('key1', {
        'id': 1,
        'author': 'author1',
        'title': 'title1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-12-01T15:15:12.376396Z',
        'updated_at': '2022-12-01T15:15:12.376396Z',
    }),
    ('new_token', None)
])
def test_show_all_recipe(key, my_result, key_for_tests):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'https://localhost:8000/api/v1/recipes', json=my_result,
              status_code=200 if key in key_for_tests else 400)
        assert my_dealer.show_all_recipes('my_fake_token') == my_result


@pytest.mark.parametrize('key, index, status_code, my_result', [
    ('key1', 1, 200, {
        'id': 1,
        'author': 'author1',
        'title': 'title1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-12-01T15:15:12.376396Z',
        'updated_at': '2022-12-01T15:15:12.376396Z',
    }),
    ('my_fake_token', 2, 400, None)
])
def test_show_specific_recipe(key, index, status_code, my_result, key_for_tests):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'https://localhost:8000/api/v1/recipes/{index}', json=my_result, status_code=status_code)
        assert my_dealer.show_specific_recipe('my_fake_token', index) == my_result


@pytest.mark.parametrize('key, title, description, ingredients, result', [
    ('my_fake_token', 'title1', 'description1', {'name': 'ingredientOne', 'quantity': 1, 'unit': 'n/a'}, {
        'id': 1,
        'author': 'author1',
        'title': 'title1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-12-01T15:15:12.376396Z',
        'updated_at': '2022-12-01T15:15:12.376396Z',
    }),
    ('my_fake_token', 'title1', 'description1', {'name': 'ingredientOne', 'quantity': '1', 'unit': 'k'},
     {'ingredients': [" '2' is not a number"]})
])
def test_add_new_recipe(key, title, description, ingredients, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.post(f'https://localhost:8000/api/v1/recipes', json=result)
        assert my_dealer.add_new_recipe(key, title, description, ingredients) == result

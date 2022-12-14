from unittest.mock import patch

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
        m.post('http://localhost:8000/api/v1/auth/login/',
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
        m.post('http://localhost:8000/api/v1/auth/logout/', status_code=200 if key in key_for_tests else 400)
        assert my_dealer.logout(key) == result


@pytest.mark.parametrize('key, index, status_code, json, result', [
    ('my_fake_token', 1, 400, {'detail': 'testing'}, 'testing'),
    ('my_fake_token', 2, 204, {}, 'The recipe is cancelled!')
])
def test_delete_recipe(key, index, status_code, json, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.delete(f'http://localhost:8000/api/v1/personal-area/{index}/', status_code=status_code, json=json)
        assert my_dealer.delete_recipe(key, index) == result


@pytest.mark.parametrize('my_result',
                         ({
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
                         })
                         )
def test_right_show_all_recipe(my_result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/', json=my_result,
              status_code=200)
        assert my_dealer.show_all_recipes() == my_result


def test_wrong_show_all_recipe():
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/', json={},
              status_code=400)
        assert my_dealer.show_all_recipes() == {}


@pytest.mark.parametrize('index, status_code, my_result', [
    (1, 200, {
        'id': 1,
        'author': 'author1',
        'title': 'title1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    }),
    (2, 400, {})
])
def test_show_specific_recipe(index, status_code, my_result, key_for_tests):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/{index}/', json=my_result, status_code=status_code)
        assert my_dealer.show_specific_recipe(index) == my_result


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
        m.post(f'http://localhost:8000/api/v1/personal-area/', json=result)
        assert my_dealer.add_new_recipe(key, title, description, ingredients) == result


@pytest.mark.parametrize('status_code, my_result', [
    (200, [{
        'id': 1,
        'author': 'author1',
        'title': 'title1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    },
        {
            'id': 2,
            'author': 'author1',
            'title': 'title1',
            'description': 'description1',
            'ingredients': {
                'name': 'ingredient1',
                'quantity': 1,
                'unit': 'n/a'
            },
            'created_at': '2022-10-01',
            'updated_at': '2022-10-01',
        }
    ]),
    (400, {})
])
def test_sort_by_date(status_code, my_result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/sort-by-date/', json=my_result, status_code=status_code)
        assert my_dealer.sort_by_date() == my_result


@pytest.mark.parametrize('status_code, my_result', [
    (200, [{
        'id': 1,
        'author': 'author1',
        'title': 'title 1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    },
        {
            'id': 1,
            'author': 'author1',
            'title': 'title 2',
            'description': 'description1',
            'ingredients': {
                'name': 'ingredient1',
                'quantity': 1,
                'unit': 'n/a'
            },
            'created_at': '2022-10-01',
            'updated_at': '2022-10-01',
        }
    ]),
    (400, {})
])
def test_sort_by_title(status_code, my_result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/sort-by-title/', json=my_result, status_code=status_code)
        assert my_dealer.sort_by_title() == my_result


@pytest.mark.parametrize('my_result', [
    ([{
        'id': 1,
        'author': 'thisIsMe',
        'title': 'title 1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    },
        {
            'id': 1,
            'author': 'thisIsMe',
            'title': 'title 2',
            'description': 'description1',
            'ingredients': {
                'name': 'ingredient1',
                'quantity': 1,
                'unit': 'n/a'
            },
            'created_at': '2022-10-01',
            'updated_at': '2022-10-01',
        }
    ]),
    ({'detail': 'forbidden'})
])
def test_sort_my_recipes_by_title(my_result, key_for_tests):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/personal-area/sort-by-title/', json=my_result)
        assert my_dealer.sort_my_recipes_by_title(key_for_tests[0]) == my_result


@pytest.mark.parametrize('my_result', [
    ([{
        'id': 1,
        'author': 'thisIsMe',
        'title': 'title 1',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient1',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-10-01',
        'updated_at': '2022-10-01',
    },
        {
            'id': 1,
            'author': 'thisIsMe',
            'title': 'title 2',
            'description': 'description1',
            'ingredients': {
                'name': 'ingredient1',
                'quantity': 1,
                'unit': 'n/a'
            },
            'created_at': '2022-12-01',
            'updated_at': '2022-12-01',
        }
    ]),
    ({'detail': 'forbidden'})
])
def test_sort_my_recipes_by_date(my_result, key_for_tests):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/personal-area/sort-by-date/', json=my_result)
        assert my_dealer.sort_my_recipes_by_date(key_for_tests[0]) == my_result


@pytest.mark.parametrize('author, result', [
    ('authorA', {'detail': 'testing'}),
    ('authorB', {'detail': 'testing'})
])
def test_filter_by_author(author, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/by-author/{author}/', json=result)
        assert my_dealer.filter_by_author(author) == result


@pytest.mark.parametrize('title, result', [
    ('titleA', {'detail': 'testing'}),
    ('titleB', {'detail': 'testing'})
])
def test_filter_by_title(title, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/by-title/{title}/', json=result)
        assert my_dealer.filter_by_title(title) == result


@pytest.mark.parametrize('ingredient, result', [
    ('ingredientA', {'detail': 'testing'}),
    ('ingredientB', {'detail': 'testing'})
])
def test_filter_by_ingredient(ingredient, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1/recipes/by-ingredient/{ingredient}/', json=result)
        assert my_dealer.filter_by_ingredient(ingredient) == result


@pytest.mark.parametrize('view, my_result', [
    ('/recipes/sort-by-title/', {'detail': 'testing'}),
    ('/recipes/sort-by-date/', {'detail': 'testing'})
])
def test_get_request_only_view(view, my_result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1{view}', json=my_result)
        assert my_dealer.get_request(view) == my_result


def test_get_request_with_data_and_headers():
    with requests_mock.Mocker() as m:
        view = '/recipes/'
        my_dealer = DealerRecipes()
        m.get(f'http://localhost:8000/api/v1{view}', json={'detail': 'testing'})
        assert my_dealer.get_request(view, data={'username': 'username'},
                                     headers={'Authorization': 'Token my_token'}) == {'detail': 'testing'}


@pytest.mark.parametrize('key, returned_json, result', [
    ('token', {'detail': 'forbidden'}, 'forbidden'),
    ('token', {'type-account': 0}, 'You are logged as normal user'),
    ('token', {'type-account': 1}, 'You are logged as admin'),
    ('token', {'type-account': 2}, 'You are logged as moderator')
])
def test_what_is_my_role(key, returned_json, result):
    my_dealer = DealerRecipes()
    with patch.object(DealerRecipes, 'get_request', return_value=returned_json):
        assert my_dealer.what_is_my_role(key) == result


@pytest.mark.parametrize('key, index, my_json, result',
                         [('token', 10, {'testing': 'testing'}, {'detail': 'testing'})])
def test_update_my_recipes(key, index, my_json, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.put(f'http://localhost:8000/api/v1/personal-area/{index}/', json={'detail': 'testing'})
        assert my_dealer.update_my_recipe(key, index, my_json) == result


@pytest.mark.parametrize('username, email, password1, password2, result',
                         [('username', 'email@email.email', 'password1', 'password2',
                           'Welcome to Secure Recipe! You are now registered as a new user.')])
def test_sign_up_right(username, email, password1, password2, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.post(f'http://localhost:8000/api/v1/auth/registration/', status_code=201)
        assert my_dealer.sign_up(username, email, password1, password2) == result


@pytest.mark.parametrize('username, email, password1, password2, result',
                         [('username', 'email', 'password1', 'password2', {'email': 'email not valid'})])
def test_sign_up_wrong(username, email, password1, password2, result):
    with requests_mock.Mocker() as m:
        my_dealer = DealerRecipes()
        m.post(f'http://localhost:8000/api/v1/auth/registration/', json={'email': 'email not valid'}, status_code=400)
        assert my_dealer.sign_up(username, email, password1, password2) == result

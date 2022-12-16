from datetime import date
from getpass import getpass

import pytest
from unittest.mock import patch

from valid8 import ValidationError

from recipe.app import ApplicationForUser, main

from recipe.domain import DealerRecipes, Username, Title, Description, Name, Quantity, Unit, Password, Id, JsonHandler, \
    Recipe, Ingredient, Email


@pytest.fixture
def fixture_recipe():
    new_recipe = Recipe.Builder(Id(1), Title('title'), Username('author'), Description('description'),
                                date.today(), date.today())
    new_recipe = new_recipe.with_ingredient(Ingredient(Name('name'), Quantity(10), Unit('n/a'))).build()
    return new_recipe


@patch('builtins.input', side_effect=['0'])
@patch('builtins.print')
def test_main(mock_print, mock_input):
    main('__main__')
    mock_print.assert_any_call('Bye bye!')
    mock_print.assert_called()


@patch('builtins.input', side_effect=['2'])
@patch('builtins.print')
def test_already_login(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=True):
        new_app.run()
        mock_print.assert_called()


@patch('builtins.input', side_effect=['2', 'username1', 'password1234'])
@patch('builtins.print')
def test_login_right(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'login', return_value='Token1234'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input') as mock_read:
                with patch.object(DealerRecipes, 'what_is_my_role', return_value='You are logged as moderator'):
                    new_app.run()
                    mock_read.assert_called()
                    mock_error.assert_not_called()
                    mock_print.assert_called()


@patch('builtins.input', side_effect=['2', 0, 'username2'])
@patch('builtins.print')
def test_login_wrong(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch('getpass.getpass', side_effect=['password4321', 'password4321', 'password4321']):
        with patch.object(DealerRecipes, 'login', return_value=None):
            with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
                with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                                  side_effect=[Username('username2'), Password('password4321')]) as mock_read:
                    new_app.run()
                    mock_read.assert_called()
                    mock_error.assert_called()


@patch('builtins.input', side_effect=['15'])
@patch('builtins.print')
def test_right_logout(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'logout', return_value='Logged out!'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_not_called()


@patch('builtins.input', side_effect=['15'])
@patch('builtins.print')
def test_wrong_logout(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'logout', return_value='Logout failed!'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_called()


@patch('builtins.input', side_effect=['9', 'n'])
def test_add_new_recipe(mock_input):
    my_side_effects = [Title('title'), Description('description1'), Name('ingredient'),
                       Quantity(1), Unit('n/a')]
    my_recipe_json = {
        'id': 1,
        'author': 'thisIsMe',
        'title': 'title',
        'description': 'description1',
        'ingredients': {
            'name': 'ingredient',
            'quantity': 1,
            'unit': 'n/a'
        },
        'created_at': '2022-10-01',
        'updated_at': '2022-10-01',
    }
    my_recipe = Recipe.Builder(Id(1), Title('title'), Username('thisIsMe'), Description('description1'),
                               date.today(), date.today())
    my_recipe = my_recipe.with_ingredient(Ingredient(Name('ingredient'), Quantity(1), Unit('n/a'))).build()
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=True):
        with patch.object(DealerRecipes, 'add_new_recipe', return_value=my_recipe_json):
            with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                              side_effect=my_side_effects) as mock_read:
                with patch.object(JsonHandler, 'create_recipe_from_json', return_value=my_recipe):
                    with patch.object(Recipe, 'print') as mock_recipe_print:
                        new_app.run()
                        mock_read.assert_called()
                        mock_recipe_print.assert_called()


@patch('builtins.input', side_effect=['9'])
def test_add_new_recipe_return_error(mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=False):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_called()


@patch('builtins.input', side_effect=['10'])
def test_delete_recipe_return_error(mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=False):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_called()


@patch('builtins.input', side_effect=['14'])
def test_update_recipe_return_error(mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=False):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_called()


@patch('builtins.input', side_effect=['10', 123])
@patch('builtins.print')
def test_right_delete_recipe(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=True):
        with patch.object(DealerRecipes, 'delete_recipe', return_value='The recipe is cancelled!'):
            with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
                with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                                  return_value=Id(123)) as mock_read:
                    new_app.run()
                    mock_read.assert_called()
                    mock_error.assert_not_called()


@patch('builtins.input', side_effect=['10', 123])
@patch('builtins.print')
def test_wrong_delete_recipe(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=True):
        with patch.object(DealerRecipes, 'delete_recipe', return_value='Error during cancellation of the recipe.'):
            with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
                with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                                  return_value=Id(123)) as mock_read:
                    new_app.run()
                    mock_read.assert_called()
                    mock_error.assert_called()


@patch('builtins.input', side_effect=['3'])
@patch('builtins.print')
def test_show_all_recipes_not_list(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'show_all_recipes', side_effect=[{'message': 'testing'}]):
        new_app.run()
        mock_print.assert_called()


@patch('builtins.input', side_effect=['4'])
@patch('builtins.print')
def test_show_specific_recipe_not_detail(mock_print, mock_input, fixture_recipe):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'show_specific_recipe', side_effect=[{'title': 'testing'}]):
        with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                          return_value=Id(123)) as mock_read:
            with patch.object(JsonHandler, 'create_recipe_from_json', side_effect=[fixture_recipe]):
                with patch.object(Recipe, 'print') as mock_recipe_print:
                    new_app.run()
                    mock_print.assert_called()
                    mock_recipe_print.assert_called()


@patch('builtins.input', side_effect=['4'])
@patch('builtins.print')
def test_show_specific_recipe_detail(mock_print, mock_input, fixture_recipe):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'show_specific_recipe', side_effect=[{'detail': 'testing'}]):
        with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                          return_value=Id(123)) as mock_read:
            new_app.run()
            mock_print.assert_called()


@pytest.mark.parametrize('name, quantity, unit, expected', [(Name('name'), Quantity(10), Unit('n/a'), {
    'name': 'name',
    'quantity': 10,
    'unit': 'n/a'
})])
def test_right_convert_input_into_json_ingredient(name, quantity, unit, expected):
    assert ApplicationForUser.convert_input_into_json_ingredient(name, quantity, unit) == expected


@patch('builtins.input', side_effect=['0'])
@patch('builtins.print')
def test_run_exception(mock_print, mock_input):
    with patch.object(ApplicationForUser, '_ApplicationForUser__run', side_effect=Exception('Test')):
        ApplicationForUser().run()
    assert mock_input.mock_calls == []
    assert list(filter(lambda x: 'Error during execution!' in str(x), mock_print.mock_calls))


@patch('builtins.input', side_effect=['15'])
@patch('builtins.print')
def test_error(mock_print, mok_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'logout', return_value='Logout failed!'):
        new_app.run()
        mock_print.assert_any_call('*** ATTENTION ***')


@patch('builtins.input', side_effect=['4', ',3', '1234'])
@patch('builtins.print')
def test_read_from_input(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'show_specific_recipe', side_effect=[{'message': 'testing'}]):
        new_app.run()


@patch('builtins.input', side_effect=['2', 'username1', 'password1234'])
def test_read_from_input_with_password(mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'login', return_value='Token1234'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_not_called()


@patch('builtins.input', side_effect=['6'])
@patch('builtins.print')
def test_sort_by_title_print_recipe(mock_print, mock_input):
    my_list = [{
        'id': 1,
        'author': 'author1',
        'title': 'title',
        'description': 'description1',
        'ingredients': [{
            'name': 'ingredient',
            'quantity': 1,
            'unit': 'n/a'
        }],
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    }]
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'sort_by_title', side_effect=[my_list]):
        with patch.object(Recipe, 'print') as mock_recipe_print:
            new_app.run()
            mock_recipe_print.assert_called()


@pytest.mark.parametrize('result', ({'detail': 'testing'}))
@patch('builtins.input', side_effect=['6'])
@patch('builtins.print')
def test_sort_by_title_print_detail(mock_print, mock_input, result):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'sort_by_title', return_value=[result]):
        new_app.run()
        mock_print.assert_called()


@pytest.mark.parametrize('result', ({'detail': 'testing'}))
@patch('builtins.input', side_effect=['5'])
@patch('builtins.print')
def test_sort_by_date(mock_print, mock_input, result):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'sort_by_date', return_value=[result]):
        new_app.run()
        mock_print.assert_called()


@pytest.mark.parametrize('result', ({'detail': 'forbidden'}))
@patch('builtins.input', side_effect=['7'])
@patch('builtins.print')
def test_sort_my_recipes_by_date(mock_print, mock_input, result):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'sort_my_recipes_by_date', return_value=[result]):
        new_app.run()
        mock_print.assert_called()


@pytest.mark.parametrize('result', ({'detail': 'forbidden'}))
@patch('builtins.input', side_effect=['8'])
@patch('builtins.print')
def test_sort_my_recipes_by_title(mock_print, mock_input, result):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'sort_my_recipes_by_title', return_value=[result]):
        new_app.run()
        mock_print.assert_called()


@patch('builtins.input', side_effect=['5'])
@patch('builtins.print')
def test_sort_by_date_print_recipe(mock_print, mock_input):
    my_list = [{
        'id': 1,
        'author': 'author1',
        'title': 'title',
        'description': 'description1',
        'ingredients': [{
            'name': 'ingredient',
            'quantity': 1,
            'unit': 'n/a'
        }],
        'created_at': '2022-12-01',
        'updated_at': '2022-12-01',
    }]
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'sort_by_date', side_effect=[my_list]):
        with patch.object(Recipe, 'print') as mock_recipe_print:
            new_app.run()
            mock_recipe_print.assert_called()


@patch('builtins.input', side_effect=['11'])
@patch('builtins.print')
def test_filter_by_author(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                      return_value=Username('username')) as mock_read:
        with patch.object(DealerRecipes, 'filter_by_author', return_value={'detail': 'testing'}):
            with patch.object(ApplicationForUser, '_ApplicationForUser__print_result_from_request') as mock_app_print:
                new_app.run()
                mock_read.assert_called()
                mock_app_print.assert_called()


@patch('builtins.input', side_effect=['12'])
@patch('builtins.print')
def test_filter_by_title(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                      return_value=Title('title')) as mock_read:
        with patch.object(DealerRecipes, 'filter_by_title', return_value={'detail': 'testing'}):
            with patch.object(ApplicationForUser, '_ApplicationForUser__print_result_from_request') as mock_app_print:
                new_app.run()
                mock_read.assert_called()
                mock_app_print.assert_called()


@patch('builtins.input', side_effect=['13'])
@patch('builtins.print')
def test_filter_by_ingredient(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                      return_value=Name('name')) as mock_read:
        with patch.object(DealerRecipes, 'filter_by_ingredient', return_value={'detail': 'testing'}):
            with patch.object(ApplicationForUser, '_ApplicationForUser__print_result_from_request') as mock_app_print:
                new_app.run()
                mock_read.assert_called()
                mock_app_print.assert_called()


@patch('builtins.input', side_effect=['3'])
@patch('builtins.print')
def test_condition_in_print_from_result(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'show_all_recipes', side_effect=[{'detail': 'testing'}]):
        with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input') as mock_read:
            new_app.run()
            mock_read.assert_not_called()


@patch('builtins.input', side_effect=['14'])
@patch('builtins.print')
def test_update_recipe_wrong(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=True):
        with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                          return_value=Id(123)) as mock_read:
            with patch.object(DealerRecipes, 'show_specific_recipe', return_value={'detail': 'testing'}):
                new_app.run()
                mock_print.assert_called()


@patch('builtins.input', side_effect=['14', 'o', 'y', 'y', 'y', 'n'])
@patch('builtins.print')
def test_update_recipe_with_detail(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=True):
        with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                          side_effect=[Id(123), Title('title'), Description('description'), Name('name'),
                                       Quantity(10), Unit('n/a')]) as mock_read:
            with patch.object(JsonHandler, 'create_recipe_from_json'):
                with patch.object(DealerRecipes, 'update_my_recipe', return_value={'detail': 'testing'}):
                    with patch.object(DealerRecipes, 'show_specific_recipe', return_value={'testing': 'testing'}):
                        new_app.run()
                        mock_print.assert_called()
                        mock_read.assert_called()


@patch('builtins.input', side_effect=['14', 'n'])
@patch('builtins.print')
def test_update_recipe_with_all_inputs(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__is_logged', return_value=True):
        with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                          side_effect=[Id(123), Title('title'), Description('description'), Name('name'),
                                       Quantity(10), Unit('n/a')]) as mock_read:
            with patch.object(ApplicationForUser, '_ApplicationForUser__read_yes_or_not_from_input',
                              side_effect=['y', 'y', 'y']):
                with patch.object(JsonHandler, 'create_recipe_from_json'):
                    with patch.object(DealerRecipes, 'update_my_recipe', return_value={'testing': 'testing'}):
                        with patch.object(DealerRecipes, 'show_specific_recipe', return_value={'testing': 'testing'}):
                            new_app.run()
                            mock_print.assert_called()
                            mock_read.assert_called()


@patch('builtins.input', side_effect=['1'])
@patch('builtins.print')
def test_sign_up(mock_input, mock_print):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                      side_effect=[Username('username'), Email('secure.softare@gmail.com'),
                                   Password('password1234'), Password('password1234')]) as mock_read:
        with patch.object(DealerRecipes, 'sign_up',
                          return_value='Welcome to Secure Recipe! You are now registered as a new user.'):
            new_app.run()
            mock_print.assert_called()
            mock_read.assert_called()


@patch('builtins.input', side_effect=['1'])
@patch('builtins.print')
def test_sign_up_with_error(mock_input, mock_print):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                      side_effect=[Username('username'), Email('secure.softare@gmail.com'),
                                   Password('password1234'), Password('password12345'), Password('password1234'),
                                   Password('password1234')]) as mock_read:
        with patch.object(DealerRecipes, 'sign_up',
                          return_value={'detail': 'error_testing'}):
            with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
                new_app.run()
                mock_error.assert_called()
                mock_print.assert_called()
                mock_read.assert_called()


@patch('builtins.input', side_effect=['1', 'usr'])
@patch('builtins.print')
def test_sign_up_with_error_show_help_msg(mock_input, mock_print):
    new_app = ApplicationForUser()
    with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
        new_app.run()
        mock_error.assert_called()
        mock_print.assert_called()
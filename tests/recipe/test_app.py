import pytest
from unittest.mock import patch
from recipe.app import ApplicationForUser

from recipe.domain import DealerRecipes, Username, Title, Description, Name, Quantity, Unit, Password, Id


@patch('builtins.input', side_effect=['1', 'username1', 'password1234'])
@patch('builtins.print')
def test_login_right(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'login', return_value='Token1234'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input') as mock_read:
                new_app.run()
                mock_read.assert_called()
                mock_error.assert_not_called()


@patch('builtins.input', side_effect=['1', 'username2', 0, 'username2'])
@patch('builtins.print')
def test_login_wrong(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch('getpass.getpass', side_effect=['password4321', 'password4321', 'password4321']):
        with patch.object(DealerRecipes, 'login', return_value=None):
            with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
                with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                                  return_value=[Username('username2'), Password('password4321')]) as mock_read:
                    new_app.run()
                    mock_read.assert_called()
                    mock_error.assert_called()


@patch('builtins.input', side_effect=['6'])
@patch('builtins.print')
def test_right_logout(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'logout', return_value='Logged out!'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_not_called()


@patch('builtins.input', side_effect=['6'])
@patch('builtins.print')
def test_wrong_logout(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'logout', return_value='Logout failed!'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            new_app.run()
            mock_error.assert_called()


@pytest.mark.parametrize('side_effects', [Title('title'), Description('This is a new description!'), Name('name'),
                                          Quantity(10), Unit('n/a')])
@patch('builtins.input', side_effect=['4', 'n'])
@patch('builtins.print')
def test_add_new_recipe(mock_print, mock_input, side_effects):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'add_new_recipe', return_value={}):
        with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                          side_effect=side_effects) as mock_read:
            new_app.run()
            mock_read.assert_called()


@patch('builtins.input', side_effect=['5', 123])
@patch('builtins.print')
def test_right_delete_recipe(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'delete_recipe', return_value='The recipe is cancelled!'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                              return_value=Id(123)) as mock_read:
                new_app.run()
                mock_read.assert_called()
                mock_error.assert_not_called()


@patch('builtins.input', side_effect=['5', 123])
@patch('builtins.print')
def test_wrong_delete_recipe(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'delete_recipe', return_value='Error during cancellation of the recipe.'):
        with patch.object(ApplicationForUser, '_ApplicationForUser__error') as mock_error:
            with patch.object(ApplicationForUser, '_ApplicationForUser__read_from_input',
                              return_value=Id(123)) as mock_read:
                new_app.run()
                mock_read.assert_called()
                mock_error.assert_called()


@patch('builtins.input', side_effect=['2'])
@patch('builtins.print')
def test_show_all_recipes(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'show_all_recipes', side_effect=[{'message': 'testing'}]):
        new_app.run()
        mock_print.assert_called()


@patch('builtins.input', side_effect=['2'])
@patch('builtins.print')
def test_show_specific_recipe(mock_print, mock_input):
    new_app = ApplicationForUser()
    with patch.object(DealerRecipes, 'show_specific_recipe', side_effect=[{'message': 'testing'}]):
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

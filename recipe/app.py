import getpass
import sys
from typing import Callable, Any

from typeguard import typechecked
from valid8 import ValidationError

from .domain import DealerRecipes, Title, Description, Name, Quantity, Unit, Password, Username, Id
from .domain import JsonHandler, Email
from .menu import Menu, Entry, Description


class ApplicationForUser:
    def __init__(self):
        self.__menu = Menu.Builder(Description('Secure Recipe Application from Command Line'),
                                   auto_select=lambda: print('Welcome to Secure Recipe!')) \
            .with_entry(Entry.create('1', 'Sign up', on_selected=lambda: self.__sign_up())) \
            .with_entry(Entry.create('2', 'Login', on_selected=lambda: self.__login())) \
            .with_entry(Entry.create('3', 'Show all the recipes', on_selected=lambda: self.__show_all_recipes())) \
            .with_entry(
            Entry.create('4', 'Show a recipe given a key', on_selected=lambda: self.__show_specific_recipe())) \
            .with_entry(Entry.create('5', 'Sort all recipes by date', on_selected=lambda: self.__sort_by_date())) \
            .with_entry(Entry.create('6', 'Sort all recipes by title', on_selected=lambda: self.__sort_by_title())) \
            .with_entry(Entry.create('7', 'Sort my recipes by date',
                                     on_selected=lambda: self.__sort_my_recipes_by_date())) \
            .with_entry(Entry.create('8', 'Sort my recipes by title',
                                     on_selected=lambda: self.__sort_my_recipes_by_title())) \
            .with_entry(Entry.create('9', 'Add recipe', on_selected=lambda: self.__add_new_recipe())) \
            .with_entry(Entry.create('10', 'Delete recipe', on_selected=lambda: self.__delete_recipe())) \
            .with_entry(Entry.create('11', 'Filter by author', on_selected=lambda: self.__filter_by_author())) \
            .with_entry(Entry.create('12', 'Filter by title', on_selected=lambda: self.__filter_by_title())) \
            .with_entry(Entry.create('13', 'Filter by ingredient', on_selected=lambda: self.__filter_by_ingredient())) \
            .with_entry(Entry.create('14', 'Update an existing recipe', on_selected=lambda: self.__update_my_recipe())) \
            .with_entry(Entry.create('15', 'Log out', on_selected=lambda: self.__logout())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye bye!'), is_exit=True)) \
            .build()
        self.__dealer = DealerRecipes()
        self.__my_key = ''

    @typechecked
    def __read_from_input(self, prompt: str, builder: Callable, password: bool = False,
                          to_convert: bool = False) -> Any:
        while True:
            try:
                line = ''
                if password:
                    line = getpass.getpass(f'{prompt}: ').strip()
                else:
                    line = input(f'{prompt}: ').strip()
                if to_convert:
                    line = int(line.strip())
                res = builder(line)
                return res
            except (TypeError, ValueError, ValidationError) as e:
                self.__error(f'Invalid {prompt}.\n {e}')

    @typechecked
    def __read_yes_or_not_from_input(self, prompt: str) -> Any:
        while True:
            line = input(f'{prompt}: ').strip()
            if line == 'y' or line == 'n':
                return line
            else:
                self.__error(f'Invalid selection.')

    def __is_logged(self):
        return self.__my_key != ''

    def __what_is_my_role(self):
        return self.__dealer.what_is_my_role(self.__my_key)

    def __sign_up(self):
        input_username: Username = self.__read_from_input('Username', Username)
        input_email: Email = self.__read_from_input('Email', Email)
        input_password: Password = self.__read_from_input('Password', Password, password=True)
        input_confirm_password: Password = self.__read_from_input('Password', Password, password=True)
        while input_password != input_confirm_password:
            self.__error("Please, the passwords provided must be equal")
            input_password: Password = self.__read_from_input('Password', Password, password=True)
            input_confirm_password: Password = self.__read_from_input('Password', Password, password=True)

        result = self.__dealer.sign_up(input_username, input_email,
                                       input_password, input_confirm_password)
        if result == 'Welcome to Secure Recipe! You are now registered as a new user.':
            print(result)
        else:
            self.__error(result)

    def __login(self):
        if self.__is_logged():
            print('You are already logged.')
            return
        input_username = self.__read_from_input('Username', Username)
        input_password = self.__read_from_input('Password', Password, password=True)
        result = self.__dealer.login(input_username, input_password)
        if result is None:
            self.__error('Incorrect login credentials.')
        else:
            self.__my_key = result
            print(self.__what_is_my_role())

    def __logout(self):
        result = self.__dealer.logout(self.__my_key)
        if result == 'Logged out!':
            print(result)
            self.__my_key = ''
        else:
            self.__error(result)

    def __add_new_recipe(self):
        if not self.__is_logged():
            self.__error('You can not perform this action without login.')
            return
        input_title = self.__read_from_input('Title', Title)
        input_description = self.__read_from_input('Description', Description)
        ingredients = self.__read_ingredients_from_input()
        result = self.__dealer.add_new_recipe(self.__my_key, input_title, input_description, ingredients)
        self.__print_result_from_request(result)

    def __delete_recipe(self):
        if not self.__is_logged():
            self.__error('You can not perform this action without login.')
            return
        input_id = self.__read_from_input('Id', Id, to_convert=True)
        result = self.__dealer.delete_recipe(self.__my_key, input_id)
        if result == 'The recipe is cancelled!':
            print(result)
        else:
            self.__error(result)

    def __show_all_recipes(self):
        result = self.__dealer.show_all_recipes()
        self.__print_result_from_request(result)

    def __show_specific_recipe(self):
        input_id: Id = self.__read_from_input('Id', Id, to_convert=True)
        result = self.__dealer.show_specific_recipe(input_id)
        self.__print_result_from_request(result)

    def __sort_by_title(self):
        result = self.__dealer.sort_by_title()
        self.__print_result_from_request(result)

    def __sort_by_date(self):
        result = self.__dealer.sort_by_date()
        self.__print_result_from_request(result)

    def __sort_my_recipes_by_title(self):
        result = self.__dealer.sort_my_recipes_by_title(self.__my_key)
        self.__print_result_from_request(result)

    def __sort_my_recipes_by_date(self):
        result = self.__dealer.sort_my_recipes_by_date(self.__my_key)
        self.__print_result_from_request(result)

    def __filter_by_author(self):
        input_author: Username = self.__read_from_input('Username', Username)
        result = self.__dealer.filter_by_author(input_author)
        self.__print_result_from_request(result)

    def __filter_by_title(self):
        input_title: Title = self.__read_from_input('Title', Title)
        result = self.__dealer.filter_by_title(input_title)
        self.__print_result_from_request(result)

    def __filter_by_ingredient(self):
        input_ingredient_name: Name = self.__read_from_input('Name', Name)
        result = self.__dealer.filter_by_ingredient(input_ingredient_name)
        self.__print_result_from_request(result)

    def __update_my_recipe(self):
        if not self.__is_logged():
            self.__error('You can not perform this action without login.')
            return
        input_id_to_change: Id = self.__read_from_input('Id', Id, to_convert=True)
        recipe_to_change = self.__dealer.show_specific_recipe(input_id_to_change)
        if 'detail' in recipe_to_change:
            self.__error(recipe_to_change['detail'])
            return
        JsonHandler.create_recipe_from_json(recipe_to_change).print()
        print('If you want to do something digit "y", otherwise digit "n".')
        if self.__read_yes_or_not_from_input('Do you want to change the title?') == 'y':
            recipe_to_change['title'] = self.__read_from_input('Title', Title).value
        if self.__read_yes_or_not_from_input('Do you want to change the description?') == 'y':
            recipe_to_change['description'] = self.__read_from_input('Description', Description).value
        if self.__read_yes_or_not_from_input('Do you want to change the ingredients?') == 'y':
            recipe_to_change['ingredients'] = self.__read_ingredients_from_input()
        result = self.__dealer.update_my_recipe(self.__my_key, input_id_to_change, recipe_to_change)
        self.__print_result_from_request(result)

    def __read_ingredients_from_input(self):
        ingredients = []
        choose_char = 'y'
        while choose_char == 'y':
            print('Insert a new ingredient.', end='\n')
            input_name: Name = self.__read_from_input('Name', Name)
            input_quantity: Quantity = self.__read_from_input('Quantity', Quantity, to_convert=True)
            input_unit: Unit = self.__read_from_input('Unit', Unit)
            choose_char = input('If you want to insert other ingredients, type y, otherwise type anything else.')
            ingredients.append(self.convert_input_into_json_ingredient(input_name,
                                                                       input_quantity, input_unit))
        return ingredients

    @typechecked
    def __print_result_from_request(self, result: Any):
        if type(result) is list:
            for r in result:
                my_recipe = JsonHandler.create_recipe_from_json(r)
                my_recipe.print()
        else:
            if 'detail' in result:
                self.__error(result['detail'])
            elif 'title' in result:
                my_recipe = JsonHandler.create_recipe_from_json(result)
                my_recipe.print()
            else:
                self.__error(result)

    @staticmethod
    @typechecked
    def __error(error_message: str):
        print('*** ATTENTION ***')
        print(error_message)
        print('*** ATTENTION ***')

    @staticmethod
    @typechecked
    def convert_input_into_json_ingredient(name: Name, quantity: Quantity, unit: Unit) -> dict:
        json = {
            'name': name.value,
            'quantity': quantity.value,
            'unit': unit.value
        }
        return json

    def __run(self) -> None:
        self.__menu.run()

    def run(self) -> None:
        try:
            self.__run()
        except:
            print('Error during execution!', file=sys.stderr)


def main(name: str):
    if name == '__main__':
        ApplicationForUser().run()


main(__name__)

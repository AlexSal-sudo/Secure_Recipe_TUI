import getpass
import sys
from typing import Callable, Any

from valid8 import ValidationError

from .domain import DealerRecipes, Title, Description, Name, Quantity, Unit, Password, Username, Id
from .menu import Menu, Entry, Description

# TODO
# SORT BY TITLE. BY MY RECIPES (SOLO LOGGATO), BY NAME_INGREDIENT, BY AUTHOR (FORSE AGAIN LETTERE),
# UPDATE RECIPE [IN PUT] (TITLE, DESCRIZIONE, GLI INGREDIENTI )


class ApplicationForUser:
    def __init__(self):
        self.__menu = Menu.Builder(Description('Secure Recipe Application from Command Line'),
                                   auto_select=lambda: print('Welcome to Secure Recipe!')) \
            .with_entry(Entry.create('1', 'Login', on_selected=lambda: self.__login())) \
            .with_entry(Entry.create('2', 'Show all the recipes', on_selected=lambda: self.__show_all_recipes())) \
            .with_entry(Entry.create('3', 'Show a recipe given a key', on_selected=lambda: self.__show_specific_recipe())) \
            .with_entry(Entry.create('4', 'Add recipe', on_selected=lambda: self.__add_new_recipe())) \
            .with_entry(Entry.create('5', 'Delete recipe', on_selected=lambda: self.__delete_recipe())) \
            .with_entry(Entry.create('6', 'Log out', on_selected=lambda: self.__logout())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye bye!'), is_exit=True))\
            .build()
        self.__dealer = DealerRecipes()
        self.__my_key = None

    def __read_from_input(self, prompt: str, builder: Callable, password: bool = False, to_convert: bool = False) -> Any:
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
                self.__error(prompt)

    def __login(self):
        input_username = self.__read_from_input('Username', Username)
        input_password = self.__read_from_input('Password', Password, True)
        result = self.__dealer.login(input_username, input_password)
        if result is None:
            self.__error('Incorrect login credentials.')
        else:
            self.__my_key = result

    def __logout(self):
        # TODO
        # Deve essere sempre possibile slogarsi oppure deve essere accessibile questo metodo solo dopo che sei loggato?
        # CI SONO METODI CHE SI VEDONO SOLO SE SEI LOGGATO
        # Devo controllare che la key non sia null o posso dare per scontato che non lo sia dato che il metodo dovrebbe
        # vedersi solo se sono loggato
        result = self.__dealer.logout(self.__my_key)
        if result == 'Logged out!':
            print(result)
            self.__my_key = None
        else:
            self.__error(result)

    def __add_new_recipe(self):
        input_title = self.__read_from_input('Title', Title)
        input_description = self.__read_from_input('Description', Description)
        ingredients = []
        choose_char = 'y'
        while choose_char == 'y':
            print('Insert a new ingredient.', end='\n')
            input_name: Name = self.__read_from_input('Name', Name)
            input_quantity: Quantity = self.__read_from_input('Quantity', Quantity, to_convert=True)
            input_unit: Unit = self.__read_from_input('Unit', Unit)
            choose_char = input('If you want to insert other ingredients, type y, otherwise type anything else.')
            ingredients.append(self.convert_input_into_json_ingredient(input_name, input_quantity, input_unit))
        result = self.__dealer.add_new_recipe(self.__my_key, input_title.value, input_description.value, ingredients)
        print(result)

    def __delete_recipe(self):
        input_id = self.__read_from_input('Id', Id)
        result = self.__dealer.delete_recipe(self.__my_key, input_id)
        if result == 'Error during cancellation of the recipe.':
            self.__error(result)
        else:
            print(result)

    def __show_all_recipes(self):
        # TODO
        # devo validare i json che mi arrivano o posso direttamente stamparli?
        print(self.__dealer.show_all_recipes(self.__my_key))

    def __show_specific_recipe(self):
        input_id = self.__read_from_input('Id', Id)
        result = self.__dealer.show_specific_recipe(self.__my_key, input_id)
        print(result)

    @staticmethod
    def __error(error_message):
        # TODO
        # COLORARE L'ERRORE
        print('*** ATTENTION ***')
        print(error_message)
        print('*** ATTENTION ***')

    @staticmethod
    def convert_input_into_json_ingredient(name: Name, quantity: Quantity, unit: Unit):
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

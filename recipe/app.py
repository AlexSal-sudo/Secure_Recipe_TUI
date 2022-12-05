import getpass
import sys

from domain import DealerRecipes, Title, Description, Name, Quantity, Unit
from menu import Menu, Entry, Description


class ApplicationForUser:
    def __init__(self):
        self.__menu = Menu.Builder(Description('Secure Recipe Application from Command Line'),
                                   auto_select=lambda: print('Welcome to Secure Recipe!')) \
            .with_entry(Entry.create('1', 'Login', on_selected=lambda: self.__login())) \
            .with_entry(Entry.create('2', 'Show all the recipes', on_selected=lambda: self.__show_all_recipes())) \
            .with_entry(Entry.create('3', 'Show a recipe given a key', on_selected=lambda: self.__show_specific_recipe())) \
            .with_entry(Entry.create('4', 'Add recipe', on_selected=lambda: self.__add_new_recipe())) \
            .with_entry(Entry.create('5', 'Delete recipe', on_selected=lambda: self.__delete_recipe())) \
            .with_entry(Entry.create('0', 'Log out', on_selected=lambda: self.__logout()), is_exit=True) \
            .build()
        self.__dealer = DealerRecipes()
        # TODO
        # forse devo tenermi la chiave salvata?
        self.__my_key = None

    def __login(self):
        count_max_try = 0
        input_username = input('Username: ')
        input_password = getpass.getpass('Password: ')
        result = self.__dealer.login(input_username, input_password)
        # TODO
        # deve continuare a tentare di fare login finché non riesce a entrare oppure lo ributta al menù?
        while result is None and count_max_try <= 3:
            self.__error('Incorrect login, retry!')
            input_username = input('Username: ')
            input_password = getpass.getpass('Password: ')
            result = self.__dealer.login(input_username, input_password)
        if result is None:
            self.__error('Incorrect login, max number of attempts achieved.')
        else:
            self.__my_key = result

    def __logout(self):
        result = self.__dealer.logout(self.__my_key)
        print(result)
        if result == 'Logged out!':
            print('Bye bye!')
            self.__my_key = None

    def __add_new_recipe(self):
        # TODO
        # come funziona? Se l'utente sbaglia devo far reinserire l'elemento o si rompe tutto e basta?
        input_title = Title(input('Title: '))
        input_description = Description(input('Description: '))
        ingredients = []
        choose_char = 'y'
        while choose_char == 'y':
            input_name = input('Name of the ingredient: ')
            input_quantity = input('Quantity of the ingredient: ')
            input_unit = input('Unit: ')
            choose_char = input('If you want to insert other ingredients, type y, otherwise type anything else. ')
            ingredients.append(self.__convert_input_into_json_ingredient(Name(input_name),
                                                                         Quantity(int(input_quantity)),
                                                                         Unit(input_unit)))
        result = self.__dealer.add_new_recipe(self.__my_key, input_title.value, input_description.value, ingredients)
        print(result)

    def __delete_recipe(self):
        input_id = input('Id: ')
        result = self.__dealer.delete_recipe(self.__my_key, input_id)
        # TODO
        # se c'è un errore quando tenta di eliminare la ricetta lo stampo con la funzione error?
        print(result)

    def __show_all_recipes(self):
        # TODO
        # devo validare i json che mi arrivano o posso direttamente stamparli?
        print(self.__dealer.show_all_recipes(self.__my_key))

    def __show_specific_recipe(self):
        input_id = input('Id: ')
        result = self.__dealer.show_specific_recipe(self.__my_key, input_id)
        print(result)

    @staticmethod
    def __error(error_message):
        # TODO
        # anche gli errori come ValidationError o TypeError vanno gestiti con questa funzione?
        print('*** ATTENTION ***')
        print(error_message)
        print('*** ATTENTION ***')

    @staticmethod
    def __convert_input_into_json_ingredient(name: Name, quantity: Quantity, unit: Unit):
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
            print('Panic error!', file=sys.stderr)

    # TODO
    # il prof nella sua TUI app usa il metodo save, dobbiamo salvare tutto anche noi?


# TODO
# Non posso usare questo metodo per tutte gli input da linea di comando, poi come valido l'oggetto?
# Perché solo dopo che creo l'oggetto viene nel caso sollevato l'errore
#    def __insert_from_input(self, message_text) -> bool:
#     while True:
#         try:
#             input_value = input(f"{message_text} ")
#             return entry.is_exit
#         except (KeyError, TypeError, ValueError):
#             print('Invalid selection. Please, try again...')


def main(name: str):
    if name == '__main__':
        ApplicationForUser().run()


main(__name__)

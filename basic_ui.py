import sqlite3

from anpy import AbstractDataHandler
from anpy_lib.data_handling import SQLDataHandler


def prompt_menu(items, message='Select one of the following options.'):
    while True:
        print(message)
        for idx, item in enumerate(items):
            print('{}: {}'.format(idx, item))
        input_str = input('> ')
        try:
            num = int(input_str)
            if 0 <= num < len(items):
                return num
        except ValueError:
            pass
        print('Invalid input')


def create_categories(handler: AbstractDataHandler):
    while True:
        print("Please type the category names separated by commas. " +
              "Type 'quit' to exit prompt.")
        input_str = input('> ')
        if input_str == 'quit':
            return
        elif input_str:
            for category in input_str.split(','):
                handler.new_category(category)
            print('Categories created.')
            return


def active_session(handler: AbstractDataHandler):
    print()
    print('The session {} in currently running'.format(
        handler.get_most_recent_session().name))
    action = prompt_menu(['Complete', 'Invalidate', 'Quit Program'])
    if action == 0:
        print('Completed.')
        handler.complete()
    elif action == 1:
        print('Canceled.')
        handler.cancel()
    elif action == 2:
        print('Exiting...')
        exit()


def not_active_session(handler: AbstractDataHandler):
    print()
    action = prompt_menu(
        ['Start Session', 'Add Categories', 'Archive Categories',
         'Quit Program'])
    if action == 0:
        category_dict = handler.get_categories()
        categories = list(category_dict.keys())
        menu = categories + ['Back']
        sub_action = prompt_menu(menu, 'Please select a category.')
        if sub_action == len(menu) - 1:
            return
        else:
            handler.start(category_dict[categories[sub_action]])
            print('Session for {} started'.format(categories[sub_action]))
    elif action == 1:
        create_categories(handler)
    elif action == 2:
        print('Not implemented yet')
        return
    else:
        print('Exiting...')
        exit()


if __name__ == '__main__':
    DATABASE_FILE = 'data.sql'
    handler = SQLDataHandler(sqlite3.Connection(DATABASE_FILE))

    if not handler.get_categories():
        create_categories(handler)

    while True:
        if handler.is_active_session():
            active_session(handler)
        else:
            not_active_session(handler)

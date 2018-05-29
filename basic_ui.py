import datetime as dt
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


def prompt_with_default(message, default):
    print(message)
    result = input('[Default={}] > '.format(default))
    if not result:
        return default
    return result


def prompt_date(defaults: dt.datetime):
    year = int(prompt_with_default('Please select a year.', defaults.year))
    month = int(prompt_with_default('Please select a year.', defaults.month))
    day = int(prompt_with_default('Please select a day.', defaults.day))
    hour = int(prompt_with_default('Please select hour [24 hour time].',
                                   defaults.hour))
    minute = int(prompt_with_default('Please select minute.', defaults.minute))
    return dt.datetime(year, month, day, hour, minute)


def confirm(message):
    print(message)
    result = ''
    while not result or result[0] not in ['y', 'n']:
        result = input('Y/N: ').lower()
    return True if result[0] == 'y' else False

def active_session(handler: AbstractDataHandler):
    print()
    session = handler.get_most_recent_session()
    print('The session {}, started on {}, is currently running.'.format(
        session.name, session.time_start.strftime('%A at %I:%M %p')))
    action = prompt_menu(
        ['Complete', 'Complete and adjust', 'Invalidate', 'Quit Program'])
    if action == 0:
        print('Completed.')
        handler.complete()
    elif action == 1:
        print('Please enter new completion date.')
        date = prompt_date(session.time_start)
        if date < session.time_start:
            print('Invalid date.')
        elif confirm('Is {} correct?'.format(date.strftime('%A at %I:%M %p'))):
            handler.complete(date)
            print('Completed.')
        else:
            print('Cancelled.')
    elif action == 2:
        print('Canceled.')
        handler.cancel()
    elif action == 3:
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
    DATABASE_FILE = 'data.db'
    handler = SQLDataHandler(sqlite3.Connection(DATABASE_FILE))

    if not handler.get_categories():
        create_categories(handler)

    while True:
        if handler.is_active_session():
            active_session(handler)
        else:
            not_active_session(handler)

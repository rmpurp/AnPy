import os
import sqlite3
import unittest

from anpy_lib.data_handling import SQLDataHandler

DATABASE_PATH = 'anpy_test_database.db'


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        os.remove(DATABASE_PATH)

    def setUp(self):
        pass

    def test_category_persistence(self):
        handler = SQLDataHandler(sqlite3.Connection(DATABASE_PATH))
        self.assertEqual(handler.get_categories(), dict())

        handler = SQLDataHandler(sqlite3.Connection(DATABASE_PATH))
        self.assertEqual(handler.get_categories(), dict())

        subjects = 'AP Bio,AP Chem,Physics 2,Biology 101,CS 61A'.split(',')
        for subject in subjects:
            handler.new_category(subject)
        self.assertEqual(set(handler.get_categories().values()), set(subjects))

        handler = SQLDataHandler(sqlite3.Connection(DATABASE_PATH))
        self.assertEqual(set(handler.get_categories().values()), set(subjects))

    def test_category_creation(self):
        handler = SQLDataHandler(sqlite3.Connection(DATABASE_PATH))
        self.assertEqual(handler.get_categories(), dict())
        with self.assertRaises(ValueError):
            handler.new_category('')

        subjects = 'AP Bio,AP Chem,Physics 2,Biology 101,CS 61A'.split(',')
        added_subjects = set()
        for i, subject in enumerate(subjects, 1):
            with self.subTest(subject=subject):
                handler.new_category(subject)
                added_subjects.add(subject)
                self.assertEqual(set(handler.get_categories().values()),
                                 added_subjects)

        with self.assertRaises(ValueError):
            handler.new_category(' ')
        for subject in subjects:
            with self.subTest(subject=subject):
                with self.assertRaises(RuntimeError):
                    handler.new_category(subject)
        self.assertEqual(set(handler.get_categories().values()), added_subjects)

        handler.new_category('    decal     \t')
        self.assertTrue('decal' in handler.get_categories().values())


if __name__ == '__main__':
    unittest.main()

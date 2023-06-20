import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)

        # All of these aren't needed, and in fact throw an error in more recent versions of SQL Alchemy 

        # setup_db(self.app, self.database_path)
        # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO Write at least one test for each test for successful operation and for expected errors.
    """ 
    ####################################################################################################################
    # /CATEGORIES TEST CASES
    ####################################################################################################################

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["categories"]), 6)

    ####################################################################################################################
    # /QUESTIONS TEST CASES
    ####################################################################################################################

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 10)
        self.assertTrue(len(data["categories"]))
        self.assertEqual(data["current_category"], "All")

    def test_get_paginated_questions(self):
        res = self.client().get("/questions?page=2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]), 9)
    
    def test_get_out_of_bound_page(self):
        res = self.client().get("/questions?page=999")
        self.assertEqual(res.status_code, 404)

    # def test_delete_question(self):
    #     deleteId = 2
    #     res = self.client().delete(f"/questions/{deleteId}")
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(len(data["total_questions"]), 18)
    #     for question in data["questions"]:
    #         self.assertFalse(question["id"] == deleteId)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import dotenv_values


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    ####################################################################################################################
    # /CATEGORIES TEST CASES
    ####################################################################################################################

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["categories"]), 6)

    def test_cannot_post_to_categories(self):
        res = self.client().post("/categories")
        self.assertEqual(res.status_code, 405)

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

    def test_add_then_delete_question(self):
        # First add the question that will be deleted so we don't have to rebuild the db every run
        questionData = {
            'question': 'Dummy question to be deleted',
            'answer':  'Dummy answer',
            'category': 2 ,
            'difficulty': 3
        }
        mockQuestionRes = self.client().post(f"/questions", json=questionData)
        deleteId = json.loads(mockQuestionRes.data)["id"]
        res = self.client().delete(f"/questions/{deleteId}")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["total_questions"], 19)
        for question in data["questions"]:
            self.assertFalse(question["id"] == deleteId)

    def test_incomplete_question_should_not_be_added(self):
        questionData = {
            'question': 'Dummy question to be deleted',
            'answer':  'Dummy answer',
            'category': 2 ,
        }
        res = self.client().post(f"/questions", json=questionData)
        self.assertEqual(res.status_code, 422)

    def test_deleting_invalid_id_should_fail(self):
        res = self.client().delete(f"/questions/1234567")
        self.assertEqual(res.status_code, 422)

    def test_search_for_string_in_questions(self):
        res = self.client().post(f"/questions/search", json={ 'searchTerm': 'pen' })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["total_questions"], 2)
    
    def test_search_for_empty_string(self):
        res = self.client().post(f"/questions/search", json={ 'searchTerm': '' })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["total_questions"], 19)

    def test_search_for_not_found_string(self):
        res = self.client().post(f"/questions/search", json={ 'searchTerm': 'abcdefg' })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["total_questions"], 0)

    def test_search_for_category_in_questions(self):
        res = self.client().get(f"/categories/2/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["total_questions"], 4)

    def test_search_for_invalid_category(self):
        res = self.client().get(f"/categories/12345/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["total_questions"], 0)

    ####################################################################################################################
    # /QUIZ TEST CASES
    ####################################################################################################################

    def test_quiz_returns_applicable_question(self):
        res = self.client().post("/quizzes", json={ 
            'quiz_category': {'type': "Art", 'id': "2"},
            'previous_questions': []
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data['question']["category"], 2)

    def test_quiz_returns_no_questions_when_category_empty(self):
        res = self.client().post("/quizzes", json={ 
            'quiz_category': {'type': "Art", 'id': "2"},
            'previous_questions': [16, 17, 18, 19]
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], None)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

########################################################################################################################
# HELPER FUNCTIONS
########################################################################################################################

# Queries the database for the catagories and formats them as expected in the frontend
def query_categories():
    rawCategories = Category.query.order_by(Category.id).all()
    categoryArray = [category.format() for category in rawCategories]
    categories = {}
    for category in categoryArray:
        categories.update(category)
    return categories

# Queries the database for the questions and categories and formats them as expected in the frontend
def query_questions(request):
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = query_categories()

    if len(current_questions) == 0 or len(categories) == 0:
        raise Exception("No questions or categories")

    return {
            "questions": current_questions,
            "total_questions": len(selection),
            "categories": categories,
            "current_category": "All"
        }

# Queries the database for all questions and returns a subset as specified by the page query param in the request
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

########################################################################################################################
# FLASK / CORS CONFIG
########################################################################################################################

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['DEBUG'] = True

    with app.app_context():
        setup_db(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS")
        return response

    # """
    # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    # """

    # """
    # @TODO: Use the after_request decorator to set Access-Control-Allow
    # """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

########################################################################################################################
# ROUTES
########################################################################################################################

    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        return jsonify({"categories": query_categories()})

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        return query_questions(request)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id: str):
        try:
            question: Question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            try:
                questions = query_questions(request)
                return {
                    "success": True,
                    "deleted": question_id,
                    "questions": questions["questions"],
                    "total_questions": questions["total_questions"],
                }
            except: abort(404)
        except: abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

########################################################################################################################
# ERROR HANDLERS
########################################################################################################################

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # @app.errorhandler(404)
    # def not_found(error):
    #     return (
    #         jsonify({"success": False, "error": 404, "message": "resource not found"}),
    #         404,
    #     )

    return app


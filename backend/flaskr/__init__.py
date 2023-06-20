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
def query_questions(request, searchTerm="", category="All"):
    selection = Question.query.order_by(Question.id).all()
    
    filteredSelection = []
    for element in selection:
        if(searchTerm.lower() in element.question.lower() and (category == 'All' or category == element.category)):
            filteredSelection.append(element)

    current_questions = paginate_questions(request, filteredSelection)
    categories = query_categories()
    print(jsonify(categories))

    return {
            "questions": current_questions,
            "total_questions": len(filteredSelection),
            "categories": categories,
            "current_category": category
        }

# Queries the database for all questions and returns a subset as specified by the page query param in the request
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

# Gets a single question which has not previously been asked, questions can also be limited to a single category
def run_quiz(previousQuestions, quizCategory):
    categoryId = quizCategory.get("id", None)
    selection = Question.query.filter_by(category = categoryId).all()

    filteredSelection = []
    for element in selection:
        if(element.id not in previousQuestions):
            filteredSelection.append(element)

    return random.choice(filteredSelection) if len(filteredSelection) > 0 else None

########################################################################################################################
# FLASK / CORS CONFIG
########################################################################################################################

    # """
    # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    # """

    # """
    # @TODO: Use the after_request decorator to set Access-Control-Allow
    # """

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

########################################################################################################################
# ROUTES
########################################################################################################################

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

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

    @app.route("/questions", methods=["POST"])
    def submit_question():
        
        try:
            body = request.get_json()
            question = body.get("question", None)
            answer = body.get("answer", None)
            category = body.get("category", None)
            difficulty = body.get("difficulty", None)

            if(question is None or answer is None or category is None or difficulty is None) :
                abort(400)
            
            question: Question = Question(question, answer, category, difficulty)
            try:
                question.insert()
                return jsonify({'success': True, "message": 'Question has been created'}), 201
            except: abort(500)
        except: abort(400)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        try:
            searchTerm = request.get_json().get("searchTerm", None)
            return query_questions(request, searchTerm)
        except: abort(400)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def retrieve_question_category(id):
        try:
            return query_questions(request, "", id)
        except: abort(400)

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

    @app.route("/quizzes", methods=["POST"])
    def retrieve_quiz():
        try:
            body = request.get_json()
            previousQuestions = body.get("previous_questions", None)
            quizCategory = body.get("quiz_category", None)
            chosenQuestion = run_quiz(previousQuestions, quizCategory)
            return {
                "question": chosenQuestion.format() if chosenQuestion else None
            }
        except: abort(400)

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
    #     return (jsonify({"success": False, "error": 404, "message": "resource not found"}), 404)

    return app


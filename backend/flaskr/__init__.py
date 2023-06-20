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

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['DEBUG'] = True

    with app.app_context():
        setup_db(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS")
        return response

########################################################################################################################
# ROUTES
########################################################################################################################

    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        return jsonify({"categories": query_categories()})

    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        questions = query_questions(request)
        
        if(len(questions.get("questions", None)) == 0):
            abort(404)

        return query_questions(request)

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id: str):
        try:
            question: Question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            questions = query_questions(request)
            return {
                "success": True,
                "deleted": question_id,
                "questions": questions["questions"],
                "total_questions": questions["total_questions"],
            }
        except: abort(422)

    @app.route("/questions", methods=["POST"])
    def submit_question():
        
        try:
            body = request.get_json()
            question = body.get("question", None)
            answer = body.get("answer", None)
            category = body.get("category", None)
            difficulty = body.get("difficulty", None)

            if(question is None or answer is None or category is None or difficulty is None) :
                abort(422)
            
            question: Question = Question(question, answer, category, difficulty)
            try:
                question.insert()
                return jsonify({'success': True, "message": 'Question has been created', 'id': question.id}), 201
            except: abort(500)
        except: abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        try:
            searchTerm = request.get_json().get("searchTerm", None)
            return query_questions(request, searchTerm)
        except: abort(422)

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def retrieve_question_category(id):
        try:
            return query_questions(request, "", id)
        except: abort(422)

    @app.route("/quizzes", methods=["POST"])
    def retrieve_quiz():
        try:
            body = request.get_json()
            previousQuestions = body.get("previous_questions", None)
            quizCategory = body.get("quiz_category", None)
            chosenQuestion = run_quiz(previousQuestions, quizCategory)
            return { "question": chosenQuestion.format() if chosenQuestion else None }
        except: abort(422)

########################################################################################################################
# ERROR HANDLERS
########################################################################################################################

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    return app


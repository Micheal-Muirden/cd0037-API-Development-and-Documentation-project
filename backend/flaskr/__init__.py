"""This module defined flask API endpoints alongside config and helper functions"""

import random
from flask import Flask, request, abort, jsonify
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

####################################################################################################
# HELPER FUNCTIONS
####################################################################################################

def query_categories():
    """Queries the database for the catagories and formats them as expected in the frontend""" 
    raw_categories = Category.query.order_by(Category.id).all()
    category_array = [category.format() for category in raw_categories]
    categories = {}
    for category in category_array:
        categories.update(category)
    return categories

def query_questions(req, search_term=None, category="All"):
    """Queries the database for the questions and categories and formats them as expected in the
    frontend"""
    selection = Question.query.order_by(Question.id).all()
    filtered_selection = []
    for element in selection:
        # The element is only included if the category is all or if the element's category matches
        if(category == 'All' or category == element.category):
            # Then if the searchTerm is not defined or it matches it can be added
            if(search_term is None or search_term.lower() in element.question.lower()):
                filtered_selection.append(element)

    current_questions = paginate_questions(req, filtered_selection)
    categories = query_categories()

    return {
            "questions": current_questions,
            "total_questions": len(filtered_selection),
            "categories": categories,
            "current_category": category
        }

def paginate_questions(req, selection):
    """Queries the database for all questions and returns a subset as specified by the page query 
    param in the request"""
    page = req.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def run_quiz(previous_questions, quiz_category):
    """Gets a single question which has not previously been asked, questions can also be limited 
    to a single category"""
    category_id = quiz_category.get("id", None)
    selection = Question.query.filter_by(category = category_id).all()

    filtered_selection = []
    for element in selection:
        if element.id not in previous_questions:
            filtered_selection.append(element)

    return random.choice(filtered_selection) if len(filtered_selection) > 0 else None

####################################################################################################
# FLASK / CORS CONFIG
####################################################################################################

def create_app():
    """create and configure the app"""
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

####################################################################################################
# ROUTES
####################################################################################################

    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        try:
            return jsonify({"categories": query_categories()})
        except Exception:
            abort(500)

    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        try:
            questions = query_questions(request)
            if len(questions.get("questions", None)) == 0:
                abort(404)
            return query_questions(request)
        except Exception:
            abort(500)

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
        except Exception:
            abort(422)

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
                return jsonify(
                    {'success': True,
                     "message": 'Question has been created', 
                     'id': question.id}), 201
            except Exception:
                abort(500)
        except Exception:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        try:
            search_term = request.get_json().get("searchTerm", None)
            return query_questions(request, search_term)
        except Exception:
            abort(422)

    @app.route("/categories/<int:question_id>/questions", methods=["GET"])
    def retrieve_question_category(question_id):
        try:
            return query_questions(request, "", question_id)
        except Exception:
            abort(422)

    @app.route("/quizzes", methods=["POST"])
    def retrieve_quiz():
        try:
            body = request.get_json()
            previous_questions = body.get("previous_questions", None)
            quiz_category = body.get("quiz_category", None)
            chosen_question = run_quiz(previous_questions, quiz_category)
            return { "question": chosen_question.format() if chosen_question else None }
        except Exception:
            abort(422)

####################################################################################################
# ERROR HANDLERS
####################################################################################################

    @app.errorhandler(404)
    def not_found():
        return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404

    @app.errorhandler(422)
    def unprocessable():
        return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422

    @app.errorhandler(400)
    def bad_request():
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(500)
    def unspecified():
        return jsonify({"success": False, "error": 500, "message": "Unspecified server error"}), 500

    return app

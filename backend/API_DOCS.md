## API Reference

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys.

#### Installing dependencies
- From the base directory open a terminal and cd into ./frontend and run the command `npm run install` to have NPM download dependencies for the frontend code
- From the base directory open a terminal and cd into ./backend and run the command `npm run install` to have PIP download dependance for the backend code

#### Starting the UI and backend
- From the base directory open a terminal and cd into ./frontend and run the command `npm run start` to serve the frontend, it should reload on change to it's source code
- From the base directory open a terminal and cd into ./backend and run the command `npm run start` to serve the backend, it should reload on change to it's source code

#### Testing the backend
- From the base directory open a terminal and cd into ./backend and run the command `npm run test` to run the unittests for the backend

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 

### Endpoints 

`GET '/categories'`

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

```json
{
  "1": "Science",
  "2": "Art",
  "3": "Geography",
  "4": "History",
  "5": "Entertainment",
  "6": "Sports"
}

```
`GET '/questions'`

- Fetches an array of Question objects from the database. Results are paginated with a default of 10 questions per page
- Request Arguments: page=<int>, used for pagination. Will return 404 if the page does not exist
- Returns: An object with the properties `categories`, `current_category`, `questions`, and `total_questions`

```json
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": "All",
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Tom Cruise",
            "category": 5,
            "difficulty": 4,
            "id": 4,
            "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        },
        ... 8 More entries
    ],
    "total_questions": 18
}
```

`DELETE '/questions/<int:question_id>'`

- Removes the question with the question_id from the database.
- Request Arguments: None
- Returns: An object with the properties `deleted`, `questions`, `success`, and `total_questions` where deleted refers 
to the id that was removed, and the questions now list a new batch of paginated questions.

```json
{
    "deleted": 4,
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Maya Angelou",
            "category": 4,
            "difficulty": 2,
            "id": 5,
            "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
        },
        ... 8 More entries
    ],
    "success": true,
    "total_questions": 17
}
```

`POST '/questions'`

- Allows a user to add to the pool of questions that are stored in the database
- Request Arguments: None
- Request Body: 

```json
{
    "question": "New question text",
    "answer": "answer text",
    "difficulty": 1,
    "category": "4"
}
```

- Returns: A message that lists the id of the new question 

```json
{
    "id": 25,
    "message": "Question has been created",
    "success":true
}
```

`GET '/questions/search'`

- Fetches all of the questions that have question text that contains the search substring
- Request Arguments: None
- Request Body: 

```json
{
    "searchTerm": "pen"
}
```
- Returns: An object with the properties `categories`, `current_category`, `questions`, and `total_questions` where
the array in questions contains paginated questions matching the provided searchTerm.

```json
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": "All",
    "questions": [
        {
            "answer": "Edward Scissorhands",
            "category": 5,
            "difficulty": 3,
            "id": 6,
            "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        },
        {
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3,
            "id": 21,
            "question": "Who discovered penicillin?"
        }
    ],
    "total_questions": 2
}
```

`GET '/categories/<int:id>/questions'`

- Gets all questions the match the category <id> 
- Request Arguments: id=<int>, a number that maps to one of the categories (ie 2 = Art)
- Returns: an object with the properties `categories`, `current_category`, `questions`, `total_questions` where questions lists 
paginated questions of the specified category

```json
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": 1,
    "questions": [
        {
            "answer": "The Liver",
            "category": 1,
            "difficulty": 4,
            "id": 20,
            "question": "What is the heaviest organ in the human body?"
        },
        {
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3,
            "id": 21,
            "question": "Who discovered penicillin?"
        },
        {
            "answer": "Blood",
            "category": 1,
            "difficulty": 4,
            "id": 22,
            "question": "Hematology is a branch of medicine involving the study of what?"
        }
    ],
    "total_questions": 3
}
```

`POST '/quizzes'`

- Returns a single question from the selected category without repeating previously completed questions, returns None 
when there are no more applicable questions to return to indicate the end of the quiz.
- Request Arguments: None
- Request Body: 

```json
{
    "previous_questions": [ 18 ],
    "quiz_category": {
        "type": "Art",
        "id": "2"
    }
}
```
- Returns: An object with the question property that contains the data for the current question, or question: None

```json
{
    "question": {
        "answer": "One",
        "category": 2,
        "difficulty": 4,
        "id": 18,
        "question": "How many paintings did Van Gogh sell in his lifetime?"
    }
}

```
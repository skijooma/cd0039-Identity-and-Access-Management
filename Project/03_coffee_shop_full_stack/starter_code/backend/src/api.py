import sys

from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from .database.models import setup_db, db_drop_and_create_all, db, Drink
from .auth.auth import requires_auth, AuthError

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# with app.app_context():
#     db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
@requires_auth("get:drinks")
def get_drinks(jwt):
    drinks = db.session.query(Drink).all()

    if len(drinks) == 0:
        abort(404)

    drinks = [drink.short() for drink in drinks]  # Format each drink to a
    # short description.

    return jsonify({'success': True, "drinks": drinks})


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    drinks = db.session.query(Drink).all()

    if len(drinks) == 0:
        abort(404)

    drinks = [drink.long() for drink in drinks]  # Format each drink to a
    # long description.

    return jsonify({'success': True, "drinks": drinks})


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
        where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drinks(jwt):
    print("IN POST DRINK => ")
    drink = []

    title = request.get_json()['title']
    recipe = request.get_json()['recipe']

    try:
        new_drink = Drink(Drink(title=title, recipe=recipe))

        # new_drink = Drink(Drink(
        #     title='cola',
        #     recipe='[{"name": "cola", "color": "black", "parts": 1}]'
        # ))

        new_drink.insert()
        drink.append(new_drink.long)

        return jsonify({'success': True, "drinks": drink})
    except:
        abort(422)
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drinks(jwt, id):
    print("PATCH +> ", request.get_data())
    drink = []

    # title = request.get_json()['title']
    # recipe = request.get_json()['recipe']

    title = 'espresso',
    recipe = '[{"name": "espresso", "color": "black", "parts": 1}]'

    try:
        updated_drink = db.session.query(Drink).filter(Drink.id == id).first()
        if updated_drink is None:
            abort(404)

        updated_drink.title = title
        updated_drink.recipe = recipe

        updated_drink.update()
        drink.append(updated_drink.long())

        return jsonify({'success': True, "drinks": drink})
    except:
        abort(422)
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(jwt, id):
    try:
        drink = db.session.query(Drink).filter(Drink.id == id).first()
        print("DELETE DRINK +> ", drink)
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({'success': True, "delete": id})
    except:
        abort(422)
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()


# Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, "error": 404, "message": "Resource not found"
    }), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False, "error": 405, "message": "Method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, "error": 422, "message": "Unprocessable entity"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False, "error": 500, "message": "Internal server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False, "error": error.status_code, "message": error.error
    }), error.status_code

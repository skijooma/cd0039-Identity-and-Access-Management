import sys

from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from .database.models import setup_db, db_drop_and_create_all, db, Drink
from .auth.auth import requires_auth, AuthError

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
Uncommenting the following lines initializes the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add two
'''

# with app.app_context():
#     db_drop_and_create_all()


# ROUTES
'''
Implementation of endpoint
    GET /drinks
        it's a public endpoint
        it contains only the drink.short() data representation
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
Implementation of endpoint
    GET /drinks-detail
        it requires the 'get:drinks-detail' permission
        it contains the drink.long() data representation
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
Implementation of endpoint
    POST /drinks
        it creates a new row in the drinks table
        it requires the 'post:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
        where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drinks(jwt):
    print("IN POST /drink => ", request.get_json())
    drink = []

    title = request.get_json()['title']
    recipe = request.get_json()['recipe']

    try:
        # new_drink = Drink(title=title, recipe=recipe)

        new_drink = Drink(
            title='coca cola',
            recipe='[{"name": "coca cola", "color": "black", "parts": 1}]'
        )

        new_drink.insert()
        drink.append(new_drink.long())

        return jsonify({'success': True, "drinks": drink})
    except:
        abort(422)
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()


'''
Implementation of endpoint
    PATCH /drinks/<id>
        <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it updates the corresponding row for <id>
        it requires the 'patch:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drinks(jwt, id):
    print("PATCH /drinks => ", request.get_json())
    drink = []

    title = request.get_json()['title']
    recipe = request.get_json()['recipe']

    # title = 'espresso',
    # recipe = '[{"name": "espresso", "color": "black", "parts": 1}]'

    try:
        updated_drink = db.session.query(Drink).filter(Drink.id == id).first()

        if updated_drink is None:
            abort(404)

        updated_drink = updated_drink.long()

        updated_drink['title'] = title
        updated_drink['recipe'] = recipe

        updated_drink.update()
        drink.append(updated_drink)

        return jsonify({'success': True, "drinks": drink})
    except:
        abort(422)
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()


'''
Implementation of endpoint
    DELETE /drinks/<id>
        <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it deletes the corresponding row for <id>
        it requires the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(jwt, id):
    try:
        drink = db.session.query(Drink).filter(Drink.id == id).first()
        print("DELETE /drink => ", drink)

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
Implementation of error handlers using the @app.errorhandler(error) decorator
    each error handler returns (with appropriate messages):
             For example:
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
Implementation of error handler for 404
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, "error": 404, "message": "Resource not found"
    }), 404


'''
Implementation of error handler for 405
'''


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False, "error": 405, "message": "Method not allowed"
    }), 405


'''
Implementation of error handler for 422
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, "error": 422, "message": "Unprocessable entity"
    }), 422


'''
Implementation of error handler for 500
'''


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False, "error": 500, "message": "Internal server error"
    }), 500


'''
Implement of error handler for AuthError
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False, "error": error.status_code, "message": error.error
    }), error.status_code

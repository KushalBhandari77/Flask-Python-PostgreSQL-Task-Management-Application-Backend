from urllib.parse import quote_plus
from flask import Flask, jsonify, request, make_response
from database import db, TaskModel

app = Flask(__name__)
# Encode the password
password = "12345"
encoded_password = quote_plus(password)

# Construct the connection string
app.config['SQLALCHEMY_DATABASE_URI']  = f"postgresql://postgres:{encoded_password}@localhost/dcc_task_management"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

def make_json_response(data, status_code):
    response = make_response(jsonify(data),status_code)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = TaskModel.query.all()
    data = [task.serialize() for task in tasks]
    return make_json_response({'success':True,'statusCode': 200, 'data': data}, 200)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return make_json_response({'success':False,'statusCode': 404, 'message': 'Task not found'}, 404)
    return make_json_response({'success':True,'statusCode': 200, 'data': task.serialize()}, 200)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = TaskModel(title=data['title'], description=data['description'], completed=data.get('completed', False))
    db.session.add(new_task)
    db.session.commit()
    return make_json_response({'success':True,'statusCode': 200, 'data': new_task.serialize()}, 200)

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return make_json_response({'success':False,'statusCode': 404, 'message': 'Task not found'}, 404)
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return make_json_response({'success':True,'statusCode': 200, 'data': task.serialize()}, 200)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return make_json_response({'success':False,'statusCode': 404, 'message': 'Task not found'}, 404)
    db.session.delete(task)
    db.session.commit()
    return make_json_response({'success':True,'statusCode': 200, 'message': 'Task deleted successfully'}, 200)

if __name__ == '__main__':
    app.run(debug=True)

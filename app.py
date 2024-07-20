from flask import Flask, request, g, jsonify
from database import *
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = 'password'

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({'message' : 'Authentication failed!'}), 403
    return decorated

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/member', methods=["GET", "POST"])
@protected
def get_member():
    if request.method == "GET":
        db = get_db()
        members_cur = db.execute('select id, name, email, level from members')
        members = members_cur.fetchall()

        return_values = []

        for member in members:
            member_dict = {}
            member_dict['id'] = member['id']
            member_dict['name'] = member['name']
            member_dict['email'] = member['email']
            member_dict['level'] = member['level']

            return_values.append(member_dict)

        return jsonify({'members' : return_values})
      
    if request.method == "POST":
        new_member_data = request.get_json()

        name = new_member_data['name']
        email = new_member_data['email']
        level = new_member_data['level']

        db = get_db()
        db.execute('insert into members (name, email, level) values (?, ?, ?)', [name, email, level])
        db.commit()
        member_cur = db.execute('select id, name, email, level from members where name = ?', [name])
        new_member = member_cur.fetchone()
        return jsonify({'id' : new_member['id'], 'name' : new_member['name'], 'email' : new_member['email'], 'level' : new_member['level']})
      
@app.route('/member/<int:member_id>', methods=["GET", "PATCH", "DELETE"])
@protected
def get_member_by_id(member_id):
    if request.method == "GET":
        db = get_db()
        member_cur = db.execute('select id, name, email, level from members where id = ?', [member_id])
        member = member_cur.fetchone()

        return jsonify({'member' : {'id' : member['id'], 'name' : member['name'], 'email' : member['email'], 'level' : member['level']}})

    if request.method == "PATCH":
        new_member_data = request.get_json()

        name = new_member_data['name']
        email = new_member_data['email']
        level = new_member_data['level']

        db = get_db()
        db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
        db.commit()

        member_cur = db.execute('select id, name, email, level from members where id = ?', [member_id])
        member = member_cur.fetchone()

        return jsonify({'member' : {'id' : member['id'], 'name' : member['name'], 'email' : member['email'], 'level' : member['level']}})

    if request.method == "DELETE":
        db = get_db()
        db.execute('delete from members where id = ?', [member_id])
        db.commit()
        return jsonify({"message":"successfully deleted"})

if __name__  == "__main__":
    app.run(debug=True)
import os
import sys
import json
import urllib2
from datetime import datetime, timedelta, date, time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
from flask_marshmallow import Marshmallow

dir_path = os.path.dirname(os.path.realpath(__file__))

if os.environ.get('APP_ENV') == 'prod':
    POSTGRES = {
        'user': 'xhsyearlunhtec',
        'pw': '4b8a9a674ec67c2f43028c78ccb2c7f874f6ac8bfd41ad0f43d37d274d6ad31e',
        'db': 'd3trkhn3atsq5g',
        'host': 'ec2-54-225-96-191.compute-1.amazonaws.com',
        'port': '5432',
    }
elif os.environ.get('APP_ENV') == 'test':
    POSTGRES = {
        'user': 'postgres',
        'pw': 'temp123321',
        'db': 'students',
        'host': 'localhost',
        'port': '5432',
    }
else:
    print('Problem getting environment. Please set APP_ENV to "test" or "prod".')
    sys.exit()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Student(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200))
    pin = db.Column(db.String(10))

    def __init__(self, name, city, addr,pin):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin

    def update(self, key, value):
        self.__dict__[key] = value


class StudentSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name', 'city', 'addr', 'pin')


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

# default endpoint
@app.route("/", methods=["GET"])
def empty_view():
    return ('move along, nothing to see here...', 200)


@app.route("/student/", methods=["POST"])
def add_student():
    name = request.json['name']
    city = request.json['city']
    addr = request.json['addr']
    pin = request.json['pin']

    new_student = Student(name, city, addr, pin)

    db.session.add(new_student)
    db.session.commit()

    return jsonify({'result': 'success'}), 201


@app.route("/student/", methods=["GET"])
def get_students():
    try:
        students = Student.query.all()
        result = students_schema.dump(students)
        return jsonify(result.data)
    except Exception as e:
        return jsonify({'result': 'error'}), 500


@app.route("/student/<int:id>", methods=["PUT"])
def student_update(id):
    try:
        student_id = Student.query.get(id)
        for key in request.json:
            student_id.update(key, request.json[key])
            flag_modified(student_id, key)

        db.session.merge(student_id)
        db.session.commit()
        return jsonify({'result': 'success'}), 201
    except Exception as e:
        return jsonify({'result': 'error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

from flask import Flask, request
from RealEstateManager import dbengine as db
from RealEstateManager.dbengine import Building, Owner
import json


app = Flask(__name__)
sess = db.RealEstateDbSession("data.db")

curr_user = None


@app.route('/')
def hello_world():
    return 'Home Page'


@app.route('/building/<building_id>')
def get_building(building_id):
    rslt = sess.get_building(Building(building_id=building_id))
    return json.dumps(rslt.__dict__) if rslt else "building not found"


@app.route('/buildings')
def get_all_buildings():
    return json.dumps(list(x.__dict__ for x in sess.get_buildings(None)))


@app.route('/owner/<owner_id>')
def get_owner(owner_id):
    rslt = sess.get_owner(Owner(owner_id=owner_id))
    return json.dumps(rslt.__dict__) if rslt else "owner not found"


@app.route('/owners')
def get_all_owners():
    return json.dumps(list(x.__dict__ for x in sess.get_owners(None)))


@app.route('/login', methods=["GET"])
def login():
    global curr_user
    rslt = sess.get_owner(Owner(owner_id=request.args["owner_id"]))
    if rslt:
        curr_user = rslt
        return "Logged in"
    else:
        return "User/owner not found"


@app.route('/building/<building_id>/delete')
def delete_building(building_id):
    rslt = sess.get_building(Building(building_id=building_id))
    if rslt:
        if not curr_user:
            return "Login first"
        if str(curr_user.owner_id) == str(rslt.owner):
            sess.delete_building(rslt)
            sess.save()
            return "Deleted Successfully"
        else:
            return "You don't have the right to delete this building !"
    else:
        return "Building not found"


@app.route('/building/<building_id>/edit', methods=["GET"])
def edit_building(building_id):
    rslt = sess.get_building(Building(building_id=building_id))
    if rslt:
        if not curr_user:
            return "login first"
        if str(curr_user.owner_id) == str(rslt.owner):
            ks = set(request.args.keys()) & set(rslt.__dict__.keys())
            pks = set(rslt.__dict__.keys()) - set(request.args.keys())
            dct = dict(map(lambda k: (k, request.args[k]), ks))
            dct.update(**dict(map(lambda k: (k, rslt.__getattribute__(k)), pks)))
            sess.update_building(Building(**dct))
            sess.save()
            return "Edited Successfully"
        else:
            return "You don't have the right to edit this building !"
    else:
        return "Building not found"


@app.route('/buildings/add', methods=["GET"])
def add_building():
    if not curr_user:
        return "Login first"
    ks = set(request.args.keys()) & set(Building().__dict__.keys())
    dct = dict(map(lambda k: (k, request.args[k]), ks))
    dct['owner'] = curr_user.owner_id
    sess.add_building(Building(**dct))
    sess.save()
    return "added !"


@app.route('/owner/<owner_id>/edit', methods=["GET"])
def edit_owner(owner_id):
    rslt = sess.get_owner(Owner(owner_id=owner_id))
    if rslt:
        if not curr_user:
            return "login first"
        if curr_user.owner_id == rslt.owner_id:
            ks = set(request.args.keys()) & set(rslt.__dict__.keys())
            pks = set(rslt.__dict__.keys()) - set(request.args.keys())
            dct = dict(map(lambda k: (k, request.args[k]), ks))
            dct.update(**dict(map(lambda k: (k, rslt.__getattribute__(k)), pks)))
            sess.update_owner(Owner(**dct))
            sess.save()
            return "Edited Successfully"
        else:
            return "You don't have the right to edit this user !"
    else:
        return "user not found"


@app.route('/owner/<owner_id>/delete')
def delete_owner(owner_id):
    global curr_user
    rslt = sess.get_owner(Owner(owner_id=owner_id))
    if rslt:
        if not curr_user:
            return "Login first"
        if curr_user.owner_id == rslt.owner_id:
            sess.delete_owner(rslt)
            sess.save()
            return "Deleted Successfully"
            curr_user = None
        else:
            return "You don't have the right to delete this owner !"
    else:
        return "owner not found"


@app.route('/owners/add', methods=["GET"])
def add_owner():
    ks = set(request.args.keys()) & set(Owner().__dict__.keys())
    dct = dict(map(lambda k: (k, request.args[k]), ks))
    print(request.args.keys(), Owner().__dict__.keys())
    sess.add_owner(Owner(**dct))
    sess.save()
    return "added !"



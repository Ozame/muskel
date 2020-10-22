import json
import os
import uuid
from datetime import datetime

import falcon
import marshmallow as ma
from dotenv import load_dotenv
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend
from mongoengine.errors import DoesNotExist, ValidationError

import model as mo
import security
from middleware import CORSComponent
from service import create_role, create_user

# Load environment variables from .env file
load_dotenv()
SECRET = os.getenv("SECRET")

# Authentication
auth_backend = JWTAuthBackend(
    user_loader=security.user_loader, secret_key=SECRET, auth_header_prefix="Bearer"
)
auth_middleware = FalconAuthMiddleware(auth_backend, exempt_routes=["/token"])

# Middleware that handles CORS
cors = CORSComponent()

app = application = falcon.API(middleware=[cors, auth_middleware])
app.req_options.strip_url_path_trailing_slash = True


class ExerciseResource:
    def on_get(self, req, resp):
        resp.body = mo.ExerciseSchema(many=True).dumps(mo.Exercise.objects)

    def on_get_id(self, req, resp, id):
        try:
            result = mo.Exercise.objects(uuid=id).get()
            resp.body = mo.ExerciseSchema().dumps(result)
        except DoesNotExist:
            resp.status = falcon.HTTP_404

    def on_put_id(self, req, resp, id):
        try:
            old = mo.Exercise.objects(uuid=id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        updated = mo.ExerciseSchema().load(req.media)
        updated.uuid = id
        updated.save()
        resp.body = mo.ExerciseSchema().dumps(updated)

    def on_post(self, req, resp):
        new_ex = mo.ExerciseSchema().load(req.media)
        new_ex.uuid = uuid.uuid4()
        new_ex.save()
        resp.status = falcon.HTTP_201
        resp.body = mo.ExerciseSchema().dumps(new_ex)

    def on_delete_id(self, req, resp, id):
        mo.Exercise.objects(uuid=id).delete()


class TemplateResource:
    def on_get(self, req, resp):
        result = mo.WorkoutTemplateSchema(many=True).dumps(mo.WorkoutTemplate.objects)
        resp.body = result

    def on_get_id(self, req, resp, id):
        try:
            wo = mo.WorkoutTemplate.objects(uuid=id).get()
            result = mo.WorkoutTemplateSchema().dumps(wo)
            resp.body = result
        except DoesNotExist:
            resp.status = falcon.HTTP_404

    def on_get_exercises(self, req, resp, id):
        try:
            wo = mo.WorkoutTemplate.objects(uuid=id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        resp.body = mo.ExerciseSchema(many=True).dumps(wo.exercises)

    def on_put_id(self, req, resp, id):
        try:
            old = mo.WorkoutTemplate.objects(uuid=id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        updated = mo.WorkoutTemplateSchema().load(req.media)
        updated.uuid = id
        updated.save()
        resp.body = mo.WorkoutTemplateSchema().dumps(updated)

    def on_post_exercises(self, req, resp, id):
        try:
            wo = mo.WorkoutTemplate.objects(uuid=id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        e_uuid = req.media.get("exercise_uuid")
        ex = mo.Exercise.objects(uuid=e_uuid).get()
        mo.WorkoutTemplate.objects(uuid=id).update_one(add_to_set__exercises=ex)
        resp.body = mo.ExerciseSchema().dumps(ex)
        resp.status = falcon.HTTP_201

    def on_post(self, req, resp):
        new_wo = mo.WorkoutTemplateSchema().load(req.media)
        new_wo.uuid = uuid.uuid4()
        new_wo.save()
        resp.status = falcon.HTTP_201
        resp.body = mo.WorkoutTemplateSchema().dumps(new_wo)

    def on_delete_id(self, req, resp, id):
        mo.WorkoutTemplate.objects(uuid=id).delete()

    def on_delete_exercise(self, req, resp, id, e_id):
        try:
            ex = mo.Exercise.objects(uuid=e_id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        mo.WorkoutTemplate.objects(uuid=id).update_one(pull__exercises=ex)


class MoveResource:
    def on_get(self, req, resp, w_id):
        try:
            wo = mo.Workout.objects(uuid=w_id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        resp.body = mo.MoveSchema(many=True).dumps(wo.moves)

    def on_get_id(self, req, resp, w_id, m_id):
        try:
            move = mo.Move.objects(uuid=m_id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        resp.body = mo.MoveSchema().dumps(move)

    def on_put_id(self, req, resp, w_id, m_id):
        try:
            wo = mo.Move.objects(uuid=m_id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        updated = mo.MoveSchema().load(req.media)
        updated.uuid = id
        updated.save()
        resp.body = mo.MoveSchema().dumps(updated)

    def on_post(self, req, resp, w_id):
        wo = mo.Workout.objects(uuid=w_id).get()
        try:
            new_move = mo.MoveSchema().load(req.media)
            exercise = mo.Exercise.objects(uuid=req.media["exercise"]).get()
            new_move.exercise = exercise
            new_move.uuid = uuid.uuid4()
        except ma.ValidationError as err:
            raise falcon.HTTPInvalidParam("Bad parameter", err.field_name)
        new_move.save()
        wo.update(push__moves=new_move)
        resp.body = mo.MoveSchema().dumps(new_move)
        resp.status = falcon.HTTP_201

    def on_delete_id(self, req, resp, w_id, m_id):
        try:
            move = mo.Move.objects(uuid=m_id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        mo.Workout.objects(uuid=w_id).update_one(pull__moves=move)
        move.delete()


class WorkoutResource:
    def on_get(self, req, resp):
        resp.body = mo.WorkoutSchema(many=True).dumps(mo.Workout.objects)

    def on_get_id(self, req, resp, w_id):
        wo = mo.Workout.objects(uuid=w_id).get()
        if wo:
            result = mo.WorkoutSchema().dumps(wo)
        else:
            result = []
        resp.body = result

    def on_put_id(self, req, resp, w_id):
        try:
            wo = mo.Workout.objects(uuid=w_id).get()
        except DoesNotExist:
            resp.status = falcon.HTTP_404
            return
        updated = mo.WorkoutSchema().load(req.media)
        updated.uuid = w_id
        updated.save()
        resp.body = mo.WorkoutSchema().dumps(updated)

    def on_post(self, req, resp):
        new_wo = mo.WorkoutSchema().load(req.media)
        new_wo.uuid = uuid.uuid4()
        new_wo.date = datetime.now()
        new_wo.save()
        resp.body = mo.WorkoutSchema().dumps(new_wo)

    def on_delete_id(self, req, resp, w_id):
        mo.Workout.objects(uuid=w_id).delete()


class TokenResource:
    def on_post(self, req, resp):
        """Returns JWT token if login credentials are correct"""
        doc = req.media
        try:
            username = doc["username"]
            password = doc["password"]
        except KeyError:
            raise falcon.HTTPBadRequest(description="Password or username missing")
        if user := security.authenticate_user(username, password):
            token = auth_backend.get_auth_token({"username": user.username})
            resp.body = json.dumps({"token": token})
        else:
            raise falcon.HTTPBadRequest(description="Incorrect username or password")


class UserResource:
    auth = {"exempt_methods": ["POST"]}

    def on_post(self, req, resp):
        """Creates a new user"""
        doc = req.media
        username = doc["username"]
        password = doc["password"]
        if mo.User.objects(username=username).count() != 0:
            resp.status = falcon.HTTP_400
            return
        elif len(password) < 8:
            resp.status = falcon.HTTP_400
            return
        new_user = mo.create_user(username, password)
        if not new_user:
            resp.status = falcon.HTTP_400
        else:
            resp.status = falcon.HTTP_CREATED


# Resource instances
exercises = ExerciseResource()
workouts = WorkoutResource()
moves = MoveResource()
templates = TemplateResource()
token = TokenResource()
users = UserResource()

# Routing
app.add_route("/token", token)

app.add_route("/users", users)

app.add_route("/templates", templates)
app.add_route("/templates/{id}", templates, suffix="id")
app.add_route("/templates/{id}/exercises", templates, suffix="exercises")
app.add_route("/templates/{id}/exercises/{e_id}", templates, suffix="exercise")

app.add_route("/exercises", exercises)
app.add_route("/exercises/{id}", exercises, suffix="id")

app.add_route("/workouts", workouts)
app.add_route("/workouts/{w_id}", workouts, suffix="id")
app.add_route("/workouts/{w_id}/moves", moves)
app.add_route("/workouts/{w_id}/moves/{m_id}", moves, suffix="id")

if __name__ == "__main__":
    user_role = create_role("USER")
    admin_role = create_role("ADMIN")
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    admin_user = mo.User.objects(username="ADMIN")
    if admin_user.count() == 0:
        create_user(admin_username, admin_password, roles=[admin_role])

from json import dumps
from re import template
import falcon
import model as mo
import json
import uuid

app = application = falcon.API()


class ExerciseResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        exs = mo.ExerciseSchema(many=True).dumps(mo.Exercise.objects)
        resp.body = exs

    def on_get_id(self, req, resp, id):
        result = mo.Exercise.objects(uuid=id).get()
        resp.body = mo.ExerciseSchema().dumps(result)

    def on_put_id(self, req, resp, id):
        doc = req.bounded_stream.read()
        old = mo.Exercise.objects(uuid=id).get()
        updated = mo.ExerciseSchema().loads(doc)
        if old:
            updated.uuid = id
            updated.save()
        #TODO: validation errors 

    def on_post(self, req, resp):
        doc = req.bounded_stream.read()
        new_ex = mo.Exercise.from_json(doc, created=True)
        new_ex.uuid = uuid.uuid4()
        new_ex.save()

    def on_delete_id(self, req, resp, id):
        mo.Exercise.objects(uuid=id).delete()


class WorkoutResource:
    def on_get(self, req, resp):
        pass

    def on_get_workout_id(self, req, resp, w_id):
        resp.body = "joop"

    def on_put(self, req, resp):
        pass

    def on_post(self, req, resp):
        pass

    def on_delete(self, req, resp):
        pass


class MoveResource:
    def on_get(self, req, resp):
        pass

    def on_get_moves(self, req, resp, w_id):
        resp.body = "moijo"

    def on_get_move_id(self, req, resp, w_id, m_id):
        resp.body = f"{w_id} ja {m_id}"

    def on_put(self, req, resp):
        pass

    def on_post(self, req, resp):
        pass

    def on_delete(self, req, resp):
        pass


class TemplateResource:
    def on_get(self, req, resp):
        pass

    def on_get_id(self, req, resp, id):
        pass

    def on_put(self, req, resp):
        pass

    def on_post(self, req, resp):
        pass

    def on_delete(self, req, resp):
        pass


# Resource instances
exercises = ExerciseResource()
workouts = WorkoutResource()
moves = MoveResource()
templates = TemplateResource()

# Routing
app.add_route("/exercises", exercises)
app.add_route("/exercises/{id}", exercises, suffix="id")
app.add_route("/workouts", workouts)
app.add_route("/workouts/{w_id}", workouts, suffix="workout_id")
app.add_route("/workouts/{w_id}/moves", moves, suffix="moves")
app.add_route("/workouts/{w_id}/moves/{m_id}", moves, suffix="move_id")
app.add_route("/templates", templates)
app.add_route("/templates/{id}", templates, suffix="id")
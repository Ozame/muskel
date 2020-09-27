from datetime import datetime
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
        # TODO: validation errors

    def on_post(self, req, resp):
        doc = json.load(req.bounded_stream)
        new_ex = mo.Exercise(doc)
        new_ex.uuid = uuid.uuid4()
        new_ex.save()

    def on_delete_id(self, req, resp, id):
        mo.Exercise.objects(uuid=id).delete()


class TemplateResource:
    def on_get(self, req, resp):
        result = mo.WorkoutTemplateSchema(many=True).dumps(mo.WorkoutTemplate.objects)
        resp.body = result

    def on_get_id(self, req, resp, id):
        wo = mo.WorkoutTemplate.objects(uuid=id).get()
        if wo:
            result = mo.WorkoutTemplateSchema().dumps(wo)
        else:
            result = []
        resp.body = result

    def on_put(self, req, resp):
        pass

    def on_post(self, req, resp):
        doc = json.load(req.bounded_stream)
        new_wo = mo.WorkoutTemplate(**doc)
        new_wo.uuid = uuid.uuid4()
        new_wo.save()

    def on_delete_id(self, req, resp, id):
        mo.WorkoutTemplate.objects(uuid=id).delete()


class MoveResource:
    def on_get(self, req, resp, w_id):
        wo = mo.Workout.objects(uuid=w_id)
        resp.body = mo.MoveSchema(many=True).dumps(wo.moves)

    def on_get_id(self, req, resp, w_id, m_id):
        resp.body = f"{w_id} ja {m_id}"

    def on_put(self, req, resp):
        pass

    def on_post(self, req, resp):
        pass

    def on_delete(self, req, resp):
        pass


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
        pass

    def on_post(self, req, resp):
        doc = json.load(req.bounded_stream)
        new_wo = mo.Workout(**doc)
        new_wo.uuid = uuid.uuid4()
        new_wo.date = datetime.now()
        new_wo.save()

    def on_delete_id(self, req, resp, w_id):
        mo.Workout.objects(uuid=w_id).delete()
        


# Resource instances
exercises = ExerciseResource()
workouts = WorkoutResource()
moves = MoveResource()
templates = TemplateResource()

# Routing
app.add_route("/exercises", exercises)
app.add_route("/exercises/{id}", exercises, suffix="id")
app.add_route("/workouts", workouts)
app.add_route("/workouts/{w_id}", workouts, suffix="id")
app.add_route("/workouts/{w_id}/moves", moves)
app.add_route("/workouts/{w_id}/moves/{m_id}", moves, suffix="id")
app.add_route("/templates", templates)
app.add_route("/templates/{id}", templates, suffix="id")
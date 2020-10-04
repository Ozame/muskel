from datetime import datetime
import falcon
from mongoengine.errors import DoesNotExist
import model as mo
import uuid

app = application = falcon.API()
app.req_options.strip_url_path_trailing_slash = True

# TODO reformat post to use schema loading


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

    def on_post(self, req, resp):
        doc = req.media
        new_ex = mo.Exercise(**doc)
        new_ex.uuid = uuid.uuid4()
        new_ex.save()
        resp.status = falcon.HTTP_201

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
        doc = req.media
        new_wo = mo.WorkoutTemplate(**doc)
        new_wo.uuid = uuid.uuid4()
        new_wo.save()
        resp.status = falcon.HTTP_201

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

    def on_post(self, req, resp, w_id):
        wo = mo.Workout.objects(uuid=w_id).get()
        doc = req.media
        new_move = mo.Move(**doc)
        new_move.uuid = uuid.uuid4()
        exercise = mo.Exercise.objects(uuid=doc["exercise"]).get()
        new_move.exercise = exercise
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

    def on_post(self, req, resp):
        doc = req.media
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

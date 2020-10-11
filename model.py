"""Module for models that contain data"""
from marshmallow import Schema, fields, post_load
from marshmallow.utils import EXCLUDE

from mongoengine import *
import mongoengine

connect(db="muskel", host="localhost", port=27017)


class Exercise(Document):
    uuid = UUIDField(primary_key=True)
    name = StringField(required=True, max_length=200)
    type = StringField(required=True, default="STRENGTH")
    description = StringField(default="")


class ExerciseSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    uuid = fields.UUID(dump_only=True)
    name = fields.Str()
    type = fields.Str()
    description = fields.Str()

    @post_load
    def make_Exercise(self, data, **kwargs):
        return Exercise(**data)


class WorkoutTemplate(Document):
    uuid = UUIDField(primary_key=True)
    name = StringField(required=True, max_length=200)
    exercises = ListField(ReferenceField(Exercise))


class WorkoutTemplateSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    uuid = fields.UUID(dump_only=True)
    name = fields.Str()
    exercises = fields.List(fields.Nested(ExerciseSchema))

    @post_load
    def make_WorkoutTemplate(self, data, **kwargs):
        return WorkoutTemplate(**data)


class Move(Document):
    uuid = UUIDField(primary_key=True)
    name = StringField(required=True, max_length=200)
    sets = IntField(min_value=0)
    reps = IntField(min_value=0)
    weight = IntField(min_value=0)
    notes = StringField(default="")
    exercise = ReferenceField(Exercise, reverse_delete_rule=mongoengine.CASCADE)


class MoveSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    uuid = fields.UUID(dump_only=True)
    name = fields.Str()
    sets = fields.Integer()
    reps = fields.Integer()
    weight = fields.Integer()
    notes = fields.Str()
    exercise = fields.Nested(ExerciseSchema)

    @post_load
    def make_move(self, data, **kwargs):
        return Move(**data)


class Workout(Document):
    uuid = UUIDField(primary_key=True)
    name = StringField(required=True, max_length=200)
    date = DateField()
    moves = ListField(ReferenceField(Move))


class WorkoutSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    uuid = fields.UUID(dump_only=True)
    name = fields.Str()
    date = fields.DateTime()
    moves = fields.List(fields.Nested(MoveSchema))

    @post_load
    def make_workout(self, data, **kwargs):
        return Workout(**data)
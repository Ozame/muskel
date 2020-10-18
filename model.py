"""Module for models that contain data"""
from marshmallow import Schema, fields, post_load
from marshmallow.utils import EXCLUDE

import mongoengine as me

me.connect(db="muskel", host="localhost", port=27017)


class Role(me.Document):
    uuid = me.UUIDField(primary_key=True)
    name = me.StringField(required=True, unique=True)


class User(me.Document):
    uuid = me.UUIDField(primary_key=True)
    username = me.StringField(required=True, max_length=32, unique=True)
    password = me.StringField(required=True)
    roles = me.ListField(me.ReferenceField(Role, reverse_delete_rule=me.DENY))


class Exercise(me.Document):
    uuid = me.UUIDField(primary_key=True)
    name = me.StringField(required=True, max_length=200)
    type = me.StringField(required=True, default="STRENGTH")
    description = me.StringField(default="")


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


class WorkoutTemplate(me.Document):
    uuid = me.UUIDField(primary_key=True)
    name = me.StringField(required=True, max_length=200)
    exercises = me.ListField(me.ReferenceField(Exercise, reverse_delete_rule=me.DENY))


class WorkoutTemplateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    uuid = fields.UUID(dump_only=True)
    name = fields.Str()
    exercises = fields.List(fields.Nested(ExerciseSchema))

    @post_load
    def make_WorkoutTemplate(self, data, **kwargs):
        return WorkoutTemplate(**data)


class Move(me.Document):
    uuid = me.UUIDField(primary_key=True)
    name = me.StringField(required=True, max_length=200)
    sets = me.IntField(min_value=0)
    reps = me.IntField(min_value=0)
    weight = me.IntField(min_value=0)
    notes = me.StringField(default="")
    exercise = me.ReferenceField(Exercise, reverse_delete_rule=me.DENY)


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


class Workout(me.Document):
    uuid = me.UUIDField(primary_key=True)
    name = me.StringField(required=True, max_length=200)
    date = me.DateField()
    moves = me.ListField(me.ReferenceField(Move, reverse_delete_rule=me.DENY))


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
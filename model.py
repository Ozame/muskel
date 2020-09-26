"""Module for models that contain data"""
from dataclasses import dataclass, field
from os import name
from typing import List, Any
from enum import Enum, auto
from datetime import date, datetime
from dataclasses_json import dataclass_json
from marshmallow import Schema, fields, post_load

from mongoengine import *

connect(db="muskel", host="localhost", port=27017)


class Exercise(Document):
    uuid = UUIDField(primary_key=True)
    name = StringField(required=True, max_length=200)
    type = StringField(required=True, default="STRENGTH")
    description = StringField(default="")


class ExerciseSchema(Schema):
    uuid = fields.UUID(dump_only=True)
    name = fields.Str()
    type = fields.Str()
    description = fields.Str()

    @post_load
    def make_Exercise(self, data, **kwargs):
        return Exercise(**data)

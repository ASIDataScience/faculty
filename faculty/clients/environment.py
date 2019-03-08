# Copyright 2018-2019 Faculty Science Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from collections import namedtuple

from marshmallow import fields, post_load

from faculty.clients.base import BaseSchema, BaseClient


Environment = namedtuple(
    "Environment",
    [
        "id",
        "project_id",
        "name",
        "description",
        "author_id",
        "created_at",
        "updated_at",
    ],
)


class EnvironmentSchema(BaseSchema):
    id = fields.UUID(data_key="environmentId", required=True)
    project_id = fields.UUID(data_key="projectId", required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    author_id = fields.UUID(data_key="authorId", required=True)
    created_at = fields.DateTime(data_key="createdAt", required=True)
    updated_at = fields.DateTime(data_key="updatedAt", required=True)

    @post_load
    def make_environment(self, data):
        return Environment(**data)


class EnvironmentClient(BaseClient):

    SERVICE_NAME = "baskerville"

    def list(self, project_id):
        endpoint = "/project/{}/environment".format(project_id)
        return self._get(endpoint, EnvironmentSchema(many=True))
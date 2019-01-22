# Copyright 2018-2019 ASI Data Science
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

from datetime import datetime, timedelta

import pytest
import pytz

import faculty.config
from faculty.session import (
    AccessToken,
    MemoryAccessTokenCache,
    _get_access_token,
    Session,
)


PROFILE = faculty.config.Profile(
    domain="test.domain.com",
    protocol="https",
    client_id="test-client-id",
    client_secret="test-client-secret",
)
ACCESS_TOKEN_URL = "{}://hudson.{}/access_token".format(
    PROFILE.protocol, PROFILE.domain
)
NOW = datetime.now(tz=pytz.utc)
IN_TEN_MINUTES = NOW + timedelta(minutes=10)


@pytest.fixture
def mock_datetime_now(mocker):
    datetime_mock = mocker.patch("faculty.session.datetime")
    datetime_mock.now.return_value = NOW
    return datetime_mock


@pytest.fixture
def isolated_session_cache(mocker):
    mocker.patch("faculty.session.Session._Session__session_cache", {})


def test_memory_access_token_cache(mock_datetime_now):
    cache = MemoryAccessTokenCache()
    access_token = AccessToken(token="access-token", expires_at=IN_TEN_MINUTES)
    cache.add(PROFILE, access_token)
    assert cache.get(PROFILE) == access_token


def test_memory_access_token_cache_miss(mocker, mock_datetime_now):
    cache = MemoryAccessTokenCache()
    access_token = AccessToken(token="access-token", expires_at=IN_TEN_MINUTES)
    cache.add(PROFILE, access_token)
    assert cache.get(mocker.Mock()) is None


def test_memory_access_token_cache_expired(mock_datetime_now):
    cache = MemoryAccessTokenCache()
    access_token = AccessToken(
        token="access-token", expires_at=NOW - timedelta(seconds=1)
    )
    cache.add(PROFILE, access_token)
    assert cache.get(PROFILE) is None


def test_get_access_token(requests_mock, mock_datetime_now):

    requests_mock.post(
        ACCESS_TOKEN_URL,
        json={"access_token": "access-token", "expires_in": 600},
    )

    access_token = _get_access_token(PROFILE)

    assert requests_mock.last_request.json() == {
        "client_id": PROFILE.client_id,
        "client_secret": PROFILE.client_secret,
        "grant_type": "client_credentials",
    }
    assert access_token == AccessToken(
        token="access-token", expires_at=IN_TEN_MINUTES
    )


def test_session_get(mocker, isolated_session_cache):
    mocker.patch("faculty.config.resolve_profile", return_value=PROFILE)
    access_token_cache = mocker.Mock()
    mocker.spy(Session, "__init__")

    session = Session.get(
        "arg1",
        "arg2",
        kwarg1="foo",
        kwarg2="bar",
        access_token_cache=access_token_cache,
    )

    faculty.config.resolve_profile.assert_called_once_with(
        "arg1", "arg2", kwarg1="foo", kwarg2="bar"
    )
    Session.__init__.assert_called_once_with(
        session, PROFILE, access_token_cache
    )


def test_session_get_defaults(mocker, isolated_session_cache):
    mocker.patch("faculty.config.resolve_profile", return_value=PROFILE)
    access_token_cache = mocker.Mock()
    mocker.patch(
        "faculty.session.MemoryAccessTokenCache",
        return_value=access_token_cache,
    )
    mocker.spy(Session, "__init__")

    session = Session.get()

    faculty.config.resolve_profile.assert_called_once_with()
    Session.__init__.assert_called_once_with(
        session, PROFILE, access_token_cache
    )


def test_session_get_cache(mocker, isolated_session_cache):
    mocker.patch("faculty.config.resolve_profile", return_value=PROFILE)
    access_token_cache = mocker.Mock()
    mocker.spy(Session, "__init__")

    session1 = Session.get(
        "arg", kwarg="foo", access_token_cache=access_token_cache
    )
    session2 = Session.get(
        "arg", kwarg="foo", access_token_cache=access_token_cache
    )

    assert session1 is session2

    faculty.config.resolve_profile.call_count == 1
    Session.__init__.call_count == 1


def test_session_access_token(mocker):
    access_token_cache = mocker.Mock()
    session = Session(PROFILE, access_token_cache)

    assert session.access_token() == access_token_cache.get.return_value
    access_token_cache.get.assert_called_once_with(PROFILE)


def test_session_access_token_cache_miss(mocker):
    access_token_cache = mocker.Mock()
    access_token_cache.get.return_value = None
    new_token = mocker.Mock()
    mocker.patch("faculty.session._get_access_token", return_value=new_token)

    session = Session(PROFILE, access_token_cache)

    assert session.access_token() == new_token
    access_token_cache.get.assert_called_once_with(PROFILE)
    access_token_cache.add.assert_called_once_with(PROFILE, new_token)


def test_session_service_url(mocker):
    session = Session(PROFILE, mocker.Mock())
    assert session.service_url(
        "service", "an/endpoint"
    ) == "{}://service.{}/an/endpoint".format(PROFILE.protocol, PROFILE.domain)


def test_session_service_url_default_endpoint(mocker):
    session = Session(PROFILE, mocker.Mock())
    assert session.service_url("service") == "{}://service.{}".format(
        PROFILE.protocol, PROFILE.domain
    )

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

import posixpath


class DatasetsError(Exception):
    pass


def rationalise_projectpath(path):

    # All paths should be relative to root
    path = posixpath.join("/", path)

    normed = posixpath.normpath(path)

    if path.endswith("/") and not normed.endswith("/"):
        normed += "/"

    return normed


def project_relative_path(project_root, project_path):

    project_root = rationalise_projectpath(project_root)
    project_path = rationalise_projectpath(project_path)

    if not project_path.startswith(project_root):
        tpl = "{} is not a sub path of {}"
        raise ValueError(tpl.format(project_path, project_root))

    # Remove the root
    relative_path = project_path[len(project_root) :]

    # Get rid of any leading '/'es
    relative_path = relative_path.lstrip("/")

    return relative_path


def project_parent_directories(project_path):
    """List all the directories in the tree containing this file.

    Parameters
    ----------
    project_path : str
        The file to list the parent directories of

    Returns
    -------
    list of str
        The paths of the parent directories
    """

    # Ensure in assumed format - can now assume to be absolute
    project_path = rationalise_projectpath(project_path)

    # Stripping trailing slashes as if it's a directory we still just want to
    # get its parent
    dirname = posixpath.dirname(project_path.rstrip("/"))

    directories = []

    parts = dirname.split("/")
    for i_last in range(1, len(parts) + 1):
        directories.append("/".join(parts[:i_last]) + "/")

    return directories


def project_parent_directory(project_path):
    """Return project_path's parent directory
    is a file.

    Parameters
    ----------
    project_path : str
        The object's path

    Returns
    -------
    str
        The paths of the parent directories
    TODO: figure out how to mention that it may return None
    """

    # Ensure in assumed format - can now assume to be absolute
    project_path = rationalise_projectpath(project_path)

    # Stripping trailing slashes as if it's a directory we still just want to
    # get its parent
    if project_path == "/":
        return None
    else:
        return posixpath.dirname(project_path.rstrip("/"))

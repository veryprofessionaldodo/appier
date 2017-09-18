#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2017 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import shelve

from . import common
from . import config
from . import component
from . import exceptions

class Preferences(component.Component):

    def __init__(self, name = "preferences", owner = None, *args, **kwargs):
        component.Component.__init__(self, name = name, owner = owner, *args, **kwargs)
        load = kwargs.get("load", True)
        if load: self.load()

    def __getitem__(self, key):
        return self.get(key, strict = True)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def get(self, name, default = None, strict = False, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def set(self, name, value, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def delete(self, name, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def flush(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

    def clear(self, *args, **kwargs):
        raise exceptions.NotImplementedError()

class MemoryPreferences(Preferences):

    def __init__(self, name = "memory", owner = None, *args, **kwargs):
        Preferences.__init__(self, name = name, owner = owner, *args, **kwargs)

    def get(self, name, default = None, strict = False, *args, **kwargs):
        if strict: return self._preferences[name]
        return self._preferences.get(name, default)

    def set(self, name, value, *args, **kwargs):
        self._preferences[name] = value

    def delete(self, name, *args, **kwargs):
        del self._preferences[name]

    def flush(self, *args, **kwargs):
        pass

    def clear(self, *args, **kwargs):
        self._preferences.clear()

    def _load(self, *args, **kwargs):
        Preferences._load(self, *args, **kwargs)
        self._preferences = dict()

    def _unload(self, *args, **kwargs):
        Preferences._unload(self, *args, **kwargs)
        self._preferences = None

class FilePreferences(Preferences):

    def __init__(self, name = "file", owner = None, *args, **kwargs):
        Preferences.__init__(self, name = name, owner = owner, *args, **kwargs)

    def get(self, name, default = None, strict = False, *args, **kwargs):
        if strict: return self._shelve[name]
        return self._shelve.get(name, default)

    def set(self, name, value, *args, **kwargs):
        self._shelve[name] = value

    def delete(self, name, *args, **kwargs):
        del self._shelve[name]

    def flush(self, *args, **kwargs):
        self._sync()

    def db_secure(self):
        return self.db_type() == "dbm"

    def db_type(self):
        shelve_cls = type(self._shelve.dict)
        shelve_dbm = shelve_cls.__name__
        return shelve_dbm

    def _load(self, *args, **kwargs):
        Preferences._load(self, *args, **kwargs)
        self.base_path = kwargs.pop("base_path", None)
        self._ensure_path()
        self._shelve = shelve.open(
            self.preferences_path,
            protocol = 2,
            writeback = True
        )

    def _unload(self, *args, **kwargs):
        Preferences._unload(self, *args, **kwargs)
        self._shelve.close()
        self._shelve = None

    def _ensure_path(self):
        if self.base_path: return
        app_path = common.base().get_base_path()
        preferences_path = os.path.join(app_path, "preferences")
        preferences_path = config.conf("PREFERENCES_PATH", preferences_path)
        self.preferences_path = preferences_path

    def _sync(self, secure = None):
        if secure == None:
            secure = self.db_secure()
        if secure:
            self._shelve.close()
            self._open()
        else:
            self._shelve.sync()

class RedisPreferences(Preferences):
    pass

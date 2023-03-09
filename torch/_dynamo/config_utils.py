import contextlib
import copy

import dataclasses
import inspect
import os

import pickle

import tempfile
import unittest
from os.path import abspath, dirname
from types import FunctionType, ModuleType
from typing import Any, Dict, Optional, Set, Type
from unittest import mock

import torch

from . import external_utils




class ContextDecorator(contextlib.ContextDecorator):
    """
    Same as contextlib.ContextDecorator, but with support for
    `unittest.TestCase`
    """

    def __call__(self, func):
        if isinstance(func, type) and issubclass(func, unittest.TestCase):

            class _TestCase(func):
                @classmethod
                def setUpClass(cls):
                    self.__enter__()
                    try:
                        super().setUpClass()
                    except Exception:
                        self.__exit__(None, None, None)
                        raise

                @classmethod
                def tearDownClass(cls):
                    try:
                        super().tearDownClass()
                    finally:
                        self.__exit__(None, None, None)

            _TestCase.__name__ = func.__name__
            return _TestCase

        return super().__call__(func)


def patch_object(obj, name, value):
    """
    Workaround `mock.patch.object` issue with ConfigModule
    """
    if isinstance(obj, ConfigMixin):
        return obj.patch(name, value)
    return mock.patch.object(obj, name, value)

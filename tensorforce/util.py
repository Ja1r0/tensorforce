# Copyright 2017 reinforce.io. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import importlib
import numpy as np
import tensorflow as tf

from tensorforce import TensorForceError, Configuration


epsilon = 1e-6


def prod(xs):
    p = 1
    for x in xs:
        p *= x
    return p


def rank(x):
    return x.get_shape().ndims


def shape(x, unknown=-1):
    return tuple(unknown if dims is None else dims for dims in x.get_shape().as_list())


def cumulative_discount(rewards, terminals, discount):
    if discount == 0.0:
        return rewards
    cumulative = 0.0
    for n, (reward, terminal) in reversed(list(enumerate(zip(rewards, terminals)))):
        if terminal:
            cumulative = 0.0
        cumulative = reward + cumulative * discount
        rewards[n] = cumulative
    return rewards


def np_dtype(dtype):
    if dtype == 'float' or dtype == float:
        return np.float32
    elif dtype == 'int' or dtype == int:
        return np.int32
    elif dtype == 'bool' or dtype == bool:
        return np.bool_
    else:
        raise TensorForceError("Error: Type conversion from type {} not supported.".format(str(dtype)))


def tf_dtype(dtype):
    """
    Translates datatype specifications in environments into tensorflow dtypes.
    Args:
        dtype: 

    Returns:

    """
    if dtype == 'float' or dtype == float or dtype == np.float32:
        return tf.float32
    elif dtype == 'int' or dtype == int or dtype == np.int32:
        return tf.int32
    else:
        raise TensorForceError("Error: Type conversion from type {} not supported.".format(str(dtype)))


def get_function(fct, predefined=None):
    if predefined is not None and fct in predefined:
        return predefined[fct]
    elif isinstance(fct, str):
        module_name, function_name = fct.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, function_name)
    elif callable(fct):
        return fct
    else:
        raise TensorForceError("Argument {} cannot be turned into a function.".format(fct))


def get_object(obj, predefined=None, kwargs=None):
    if isinstance(obj, Configuration):
        fct = obj.type
        full_kwargs = {key: value for key, value in obj if key != 'type'}
    elif isinstance(obj, dict):
        fct = obj['type']
        full_kwargs = {key: value for key, value in obj.items() if key != 'type'}
    else:
        fct = obj
        full_kwargs = dict()
    obj = get_function(fct=fct, predefined=predefined)
    if kwargs is not None:
        full_kwargs.update(kwargs)
    return obj(**full_kwargs)

"""
General Helper Module for Flambda APP
Version: 1.0.0
"""
import hashlib
import json
import os
import sys
import traceback
from datetime import datetime
from datetime import date
from enum import Enum
from boot import get_environment as get_env

import pytz

from flambda_app.logging import get_logger, get_console_logger

TZ_AMERICA_SAO_PAULO = 'America/Sao_Paulo'


def generate_process():
    """Generates a unique hash based on the current timestamp with a default prefix.

    Returns:
        str: A hashed string derived from the current timestamp.
    """
    return generate_hash(str("default" + datetime.now().isoformat()))


def generate_hash(data):
    """Generates a SHA-256 hash for the given data.

    Args:
        data (str): The input data to be hashed.

    Returns:
        str: The SHA-256 hexadecimal digest of the input data.
    """
    event_hash = hashlib.sha256(str(data).encode()).hexdigest()
    return event_hash


def open_vendor_file(filename, mode):
    """Attempts to open a vendor file from predefined directories.

      Args:
          filename (str): The name of the file to open.
          mode (str): The mode in which to open the file.

      Returns:
          file object or None: The opened file object if found, otherwise None.
    """
    if __package__:
        current_path = os.path.abspath(
            os.path.dirname(__file__)).replace('/' + str(__package__), '', 1)
    else:
        current_path = os.path.abspath(os.path.dirname(__file__))

    directories = [
        '.',
        './vendor',
        '/opt/python/lib/python%s.%s/site-packages' % sys.version_info[:2],
        current_path
    ]

    for dirname in directories:
        full_path = os.path.join(dirname, filename)
        if os.path.isfile(full_path):
            return open(full_path, mode=mode)


def empty(where):
    """Checks if the given object is empty.

    Args:
        where (any): The object to check.

    Returns:
        bool: True if the object is empty, otherwise False.
    """
    result = False
    if isinstance(where, dict) and where == {}:
        result = True
    elif isinstance(where, list) and len(where) == 0:
        result = True
    elif isinstance(where, str) and where == '':
        result = True
    elif isinstance(where, bytes) and len(where) == 0:
        result = True
    elif where is None:
        result = True
    return result


def has_attr(object, attribute):
    """Checks if an object has a specific attribute.

    Args:
        object (any): The object to inspect.
        attribute (str): The attribute name to check.

    Returns:
        bool: True if the attribute exists, otherwise False.
    """
    try:
        if hasattr(object, attribute):
            return True
    except Exception:
        return False


def to_dict(obj, force_str=False):
    """Converts an object to a dictionary.

    Args:
        obj (object): The object to convert.
        force_str (bool, optional): Whether to force string conversion of values. Defaults to False.

    Returns:
        dict: A dictionary representation of the object.
    """
    data = obj.__dict__
    if force_str:
        return {k: str(v) for k, v in data.items() if v is not None}
    else:
        _dict = {}
        for k, v in data.items():
            if isinstance(v, Enum):
                _dict[k] = str(v)
            elif getattr(v, "to_dict", None):
                # recursivo
                _dict[k] = to_dict(v, force_str)
            else:
                _dict[k] = v
        return _dict


def to_json(obj):
    """Serializes an object to a JSON string.

    Args:
        obj (any): The object to serialize.

    Returns:
        str: The JSON string representation of the object.
    """
    return json.dumps(obj, default=str)


def debug_mode():
    """Checks if the application is running in debug mode.

    Returns:
        bool: True if debug mode is enabled, otherwise False.
    """
    result = False
    if 'DEBUG' in os.environ and str(os.getenv('DEBUG')).lower() == 'true':
        result = True
    return result


def convert_to_int(str_value):
    """
    Essa função foi criada para ser usada em loops funcionais z = [x for x in y]
    :param str_value:
    :return:
    :rtype: int
    """
    value = 0
    try:
        value = int(str_value)
    except Exception as err:
        get_logger().error(err)

    return value


def convert_to_float(str_value):
    """
    Essa função foi criada para ser usada em loops funcionais z = [x for x in y]
    :param str_value:
    :return:
    :rtype: float
    """
    value = 0
    try:
        value = float(str_value)
    except Exception as err:
        get_logger().error(err)

    return value


def datetime_now_with_timezone(timezone_name='America/Sao_Paulo'):
    """Gets the current datetime with the specified timezone.

    Args:
        timezone_name (str, optional): The timezone name. Defaults to 'America/Sao_Paulo'.

    Returns:
        datetime: The current datetime with timezone information.
    """
    return datetime.now(tz=pytz.timezone(timezone_name))


def datetime_format_for_database(datetime_object):
    """Formats a datetime object as a string for database storage.

    Args:
        datetime_object (datetime): The datetime object to format.

    Returns:
        str: The formatted datetime string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime_object.strftime('%Y-%m-%d %H:%M:%S')


def datetime_format_for_lifecycle(datetime_object):
    """Formats a datetime object in ISO 8601 format.

    Args:
        datetime_object (datetime): The datetime object to format.

    Returns:
        str: The formatted datetime string in ISO 8601 format.
    """
    return datetime_object.isoformat()


def datetime_add_timezone(datetime_object: datetime, timezone_name='America/Sao_Paulo'):
    """Adds a timezone to a naive datetime object.

    Args:
        datetime_object (datetime): The naive datetime object.
        timezone_name (str, optional): The timezone name. Defaults to 'America/Sao_Paulo'.

    Returns:
        datetime: The datetime object with the specified timezone.
    """
    return datetime.fromtimestamp(datetime_object.timestamp(), tz=pytz.timezone(timezone_name))


def datetime_convert_utc_to_local_timezone(datetime_object: datetime,
                                           timezone_name='America/Sao_Paulo'):
    """Converts a UTC datetime object to a specified local timezone.

    Args:
        datetime_object (datetime): The UTC datetime object.
        timezone_name (str, optional): The target local timezone. Defaults to 'America/Sao_Paulo'.

    Returns:
        datetime: The datetime object converted to the local timezone.
    """
    local_tz = pytz.timezone(timezone_name)
    datetime_with_timezone = datetime_object.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(datetime_with_timezone)
    # return datetime_with_timezone


def datetime_convert_local_timezone_to_utc(datetime_object: datetime,
                                           timezone_name='America/Sao_Paulo'):
    """Converts a local timezone datetime object to UTC.

    Args:
        datetime_object (datetime): The datetime object in a local timezone.
        timezone_name (str, optional): The local timezone name. Defaults to 'America/Sao_Paulo'.

    Returns:
        datetime: The UTC datetime object.
    """
    local_tz = pytz.timezone(timezone_name)
    utc_tz = pytz.utc
    datetime_with_timezone = datetime_object.replace(tzinfo=local_tz).astimezone(utc_tz)
    return utc_tz.normalize(datetime_with_timezone)
    # return datetime_with_timezone


def get_protocol():
    """Determines the protocol (HTTP or HTTPS) based on environment settings.

    Returns:
        str: 'https://' if HTTPS is enabled, otherwise 'http://'.
    """
    protocol = 'http://'
    if is_https():
        protocol = 'https://'
    return protocol


def is_https():
    """Checks if HTTPS is enabled based on environment variables.

    Returns:
        bool: True if HTTPS is enabled, otherwise False.
    """
    result = False
    if 'HTTPS' in os.environ and str(os.getenv('HTTPS')).lower() == 'true':
        result = True
    return result


def is_count_request(app):
    request = app.current_request.query_params
    return True if request is not None and (
        request.get('count') == "true" or request.get('count') == "1") else False


def print_routes(app, logger=None):
    """
    :param logger:
    :param (chalice.Chalice) app:
    :return:
    """
    if logger is None:
        logger = get_console_logger()
    logger.info('List of routes:')

    if has_attr(app, 'get_routes'):
        routes = app.get_routes()
    elif has_attr(app, 'url_map'):
        routes = {rule.rule: dict.fromkeys(rule.methods, 0) for rule in app.url_map.iter_rules()}
    else:
        routes = app.routes
    for path, dict_route in routes.items():
        methods = list(dict_route.keys())
        for method in methods:
            logger.info('Route: %s - %s', method, path)


def get_environment():
    """Retrieves the current environment setting.

    Returns:
        str: The environment name.
    """
    return get_env()


def is_running_on_lambda(force=False):
    """Checks if the application is running on AWS Lambda.

    Args:
        force (bool, optional): If True, forces the function to return True in development.
        Defaults to False.

    Returns:
        bool: True if running on AWS Lambda, otherwise False.
    """
    if get_environment() == 'development':
        return False if force is False else True
    else:
        return os.environ.get("AWS_EXECUTION_ENV") is not None


def has_method(obj, method_name):
    """Checks if an object has a callable method with the given name.

    Args:
        obj (object): The object to inspect.
        method_name (str): The method name to check.

    Returns:
        bool: True if the object has the callable method, otherwise False.
    """
    if has_attr(obj, method_name):
        method = getattr(obj, method_name, None)
        if callable(method):
            return True
        else:
            return False
    else:
        return False


def convert_object_dates_to_iso_with_timezone(target_object, timezone_name=None):
    """Converts all datetime or date attributes of an object to ISO 8601 format with timezone.

    Args:
        target_object (object): The object containing datetime or date attributes.
        timezone_name (str, optional): The timezone name to apply. Defaults to None.
    """
    attrs = [att for att in dir(target_object) if not att.startswith('__')]
    for att in attrs:
        try:
            val = getattr(target_object, att, None)
            if isinstance(val, datetime) or isinstance(val, date):
                if timezone_name:
                    val = datetime_add_timezone(val, TZ_AMERICA_SAO_PAULO)
                setattr(target_object, att, val.isoformat())
        except Exception as err:
            get_logger().error(err)


def convert_object_dates_to_iso_utc(target_object):
    """Converts all datetime attributes of an object to ISO 8601 format in UTC.

    Args:
        target_object (object): The object containing datetime attributes.
    """
    attrs = [att for att in dir(target_object) if not att.startswith('__')]
    for att in attrs:
        try:
            val = getattr(target_object, att, None)
            if isinstance(val, datetime):
                # val = datetime_add_timezone(val)
                val = datetime_convert_local_timezone_to_utc(val)
                setattr(target_object, att, val.isoformat())
        except Exception as err:
            get_logger().error(err)


def get_function_name(class_name=""):
    """Retrieves the name of the current function.

    Args:
        class_name (str, optional): The class name to prepend. Defaults to "".

    Returns:
        str: The function name, optionally prefixed by the class name.
    """
    fn_name = class_name + "::" + traceback.extract_stack(None, 2)[0][2]
    if not class_name:
        fn_name = traceback.extract_stack(None, 2)[0][2]
    return fn_name


def convert_list_to_dict(item_list, key_name):
    """Converts a list of dictionaries into a dictionary using a specified key.

    Args:
        item_list (list): A list of dictionaries.
        key_name (str): The key to use as the dictionary key.

    Returns:
        dict: A dictionary where keys are values from the specified key in the list items.
    """
    result = dict()
    if isinstance(item_list, list):
        for item in item_list:
            if isinstance(item, dict) and key_name in item.keys():
                result[item.get(key_name)] = item

    return result

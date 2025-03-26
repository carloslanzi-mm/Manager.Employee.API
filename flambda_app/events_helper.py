"""
Events Helper Module for Flambda APP
Version: 1.0.0
"""
import ast
import json

from flambda_app import helper
from flambda_app.decorators import SQSEvent
from flambda_app.decorators.events import SQSRecord
from flambda_app.logging import get_logger


def read_event(record, logger=None):
    """
    Reads an event from a given record and extracts the event body.

    Args:
        record (dict | str | object): The record containing the event.
        logger (object, optional): Logger instance. Defaults to None.

    Returns:
        dict | None: The parsed event body, or None if parsing fails.
    """
    if logger is None:
        logger = get_logger()
    logger.info(f"Trying to read event from record: {record}")
    logger.info(f"Getting type: {type(record)}")
    try:
        logger.info(f"Dump: {json.dumps(record)}")
    except Exception as err:
        logger.error(f"Failed to dump record: {err}")
    event_body = None
    try:
        if isinstance(record, dict):
            try:
                event_body = json.loads(record['body'])
            except Exception as err:
                logger.error(f"JSON decoding failed: {err}")
                unescaped_str = ast.literal_eval(record['body'])
                event_body = json.loads(unescaped_str)
        elif isinstance(record, str):
            record = json.loads(record)
            event_body = json.loads(record.body)
        elif isinstance(record.body, str):
            event_body = json.loads(record.body)
        else:
            event_body = record.body
    except Exception as err:
        logger.error(f"Error processing event body: {err}")
        logger.info(f"Event body: {event_body}")
    return event_body


def get_records_from_sqs_event(sqs_event, logger=None):
    """
    Extracts records from an SQS event.

    Args:
        sqs_event (SQSEvent | SQSRecord): The SQS event or record object.
        logger (object, optional): Logger instance. Defaults to None.

    Returns:
        list: A list of extracted records.
    """
    if logger is None:
        logger = get_logger()
    records = []
    try:
        if isinstance(sqs_event, SQSEvent):
            logger.info("SQSEvent instance detected.")
            if not helper.empty(sqs_event.to_dict()):
                try:
                    sqs_event_dict = sqs_event.to_dict()
                    if 'Records' in sqs_event_dict:
                        sqs_event_dict = sqs_event_dict['Records']
                    for record in sqs_event_dict:
                        records.append(record)
                except Exception as err:
                    logger.error(err)
                    records.append(sqs_event.to_dict())
        elif isinstance(sqs_event, SQSRecord):
            logger.info("SQSRecord instance")
            if not helper.empty(sqs_event.to_dict()):
                records.append(sqs_event)
    except Exception as err:
        logger.error(f"Unexpected error processing SQS event: {err}")
        if isinstance(sqs_event, SQSEvent) or isinstance(sqs_event, SQSRecord):
            logger.error(sqs_event.__dict__)
        else:
            try:
                logger.error(json.dumps(sqs_event))
            except Exception as err:
                logger.error(f"Error dumping sqs_event: {err}")
                logger.error(str(sqs_event))
    return records

import functools
import json


def pretty_print(logger, serializer_function=lambda obj: obj.__dict__):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            serializable_obj = func(*args, **kwargs)
            try:
                formatted_output = json.dumps(serializable_obj, indent=4, default=serializer_function)
                print(formatted_output)
            except TypeError as e:
                logger.error(f"Type Error encounter with message {e}")
                raise  # Re-throw exception to fail the program execution with stack-trace.
        return wrapper
    return decorator

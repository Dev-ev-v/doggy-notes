import typing


def _check_type(value, expected_type) -> bool:

    origin = typing.get_origin(expected_type)

    if origin is typing.Union:
        args = typing.get_args(expected_type)
        return any(_check_type(value, arg) for arg in args)

    if expected_type is type(None):
        return value is None

    if origin in (list, typing.List):
        if not isinstance(value, list):
            return False
        (item_type,) = typing.get_args(expected_type) or (typing.Any,)
        if item_type is typing.Any:
            return True
        return all(_check_type(item, item_type) for item in value)

    if isinstance(expected_type, type):
        return isinstance(value, expected_type)

    return True


def validate_fields(data: dict, cls) -> list[str]:

    hints = typing.get_type_hints(cls)
    errors = []

    for field_name, expected_type in hints.items():
        if field_name not in data:
            continue

        value = data[field_name]

        if not _check_type(value, expected_type):
            errors.append(
                f"Field '{field_name}' has a unexpected type: expected "
                f"{expected_type}, received {type(value).__name__}"
            )

    return errors
"""Validate the JSON Schema keywords used by the analysis agents."""


def validate_schema(data, schema: dict, path: str = "$") -> None:
    # ponytail: our current schema subset; use jsonschema if schemas expand.
    supported = {"type", "required", "properties", "additionalProperties", "items", "enum"}
    if schema.keys() - supported:
        raise ValueError(f"{path}: unsupported schema keywords: {schema.keys() - supported}")
    types = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
    if type(data) is not types[schema["type"]]:
        raise ValueError(f"{path}: expected {schema['type']}")
    if "enum" in schema and data not in schema["enum"]:
        raise ValueError(f"{path}: expected one of {schema['enum']}")
    if isinstance(data, dict):
        missing = set(schema.get("required", [])) - data.keys()
        if missing:
            raise ValueError(f"{path}: missing fields: {sorted(missing)}")
        properties = schema.get("properties", {})
        extra = data.keys() - properties.keys()
        if schema.get("additionalProperties") is False and extra:
            raise ValueError(f"{path}: unexpected fields: {sorted(extra)}")
        for key in data.keys() & properties.keys():
            validate_schema(data[key], properties[key], f"{path}.{key}")
    elif isinstance(data, list):
        for index, item in enumerate(data):
            validate_schema(item, schema["items"], f"{path}[{index}]")

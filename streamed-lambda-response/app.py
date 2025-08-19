from flask import (Flask, jsonify)
from flask import stream_with_context
from flask import request, Response
import json
from pydantic import BaseModel
from typing import Generator

app = Flask(__name__)

class Record(BaseModel):
    record_id: int
    attribute1: str
    long_value: str

def stream_pydantic_model(model: BaseModel, long_field: str, chunk_size: int = 1024 * 64) -> Generator[str, None, None]:
    """
    Stream a Pydantic model instance as JSON, chunking only the specified long field.
    
    Args:
        model (BaseModel): The Pydantic model instance
        long_field (str): The name of the field containing the long string
        chunk_size (int): How big each chunk of the long string should be (default: 64KB)
    
    Yields:
        str: Chunks of JSON string
    """
    print(" in stream pydantic model")
    data = model.dict()  # dict representation. todo: use model_dump() if needed
    print("made it past model dump")
    if long_field not in data:
        raise ValueError(f"Field '{long_field}' not found in model")
    print("made it past long field check")
    # Start object
    yield "{"

    # Handle all fields except the long one
    first = True
    for key, value in data.items():
        if key == long_field:
            continue

        if not first:
            yield ","
        json_key = json.dumps(key)
        json_value = json.dumps(value)
        yield f"{json_key}:{json_value}"
        first = False

    # Add the long field
    if not first:
        yield ","
    json_key = json.dumps(long_field)
    yield f"{json_key}:\""

    long_value = str(data[long_field])
    for i in range(0, len(long_value), chunk_size):
        yield long_value[i:i+chunk_size]

    yield "\"}"

@app.route("/", methods=["GET"])
def stream_large_json():
    DEBUG_REQUEST = False
    DEBUG_STREAM = True
    if DEBUG_REQUEST:
        print("request", request)
        print("--------------------------")
        print("dir(request )", dir(request))
        print("--------------------------")
        print("request environ", request.environ)
        print("--------------------------")
        print("request headers", request.headers)
        print("===============================")
        try:
            print("lets goooo")
            print("X-Amzn-Request-Context", request.headers["X-Amzn-Request-Context"])
            print("X-amazn-Lambda-Context", request.headers["X-Amzn-Lambda-Context"])
        except Exception as e:
            print("Error accessing headers:", e)

        return Response({
            "message": "Hello, World!",
        },content_type="application/json")
    if DEBUG_STREAM:

        record = Record(
            record_id=1,
            attribute1="aabc",
            long_value="a very long string of text here" * 200000
        )

        return Response(
            stream_with_context(stream_pydantic_model(record, "long_value")),
            content_type="application/json"
        )
    # return generic hello world response
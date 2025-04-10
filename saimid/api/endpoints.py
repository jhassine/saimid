"""API endpoints."""

import json
import logging
import os
import time
from collections.abc import Generator
from typing import LiteralString

import requests
from django.http import HttpRequest, StreamingHttpResponse
from ninja import NinjaAPI
from ninja.responses import Response
from openai import OpenAI

from saimid.config.prompts import (
    DEID_HEADER,
    QUOTE,
    REDACTION_SUMMARY,
    USER_RESPONSE_PROMPT,
    get_deid_prompt,
    reid_instructions,
)

TIMEOUT = 60
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")


pseudonymizer_client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
    timeout=TIMEOUT,
)

real_client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
    timeout=TIMEOUT,
)

"""Model used for de-identification."""
DEID_MODEL = "models/gemini-2.0-flash-lite"

"""Model used for chat topic summarization."""
SUMMARY_MODEL = "models/gemma-3-27b-it"


api = NinjaAPI()
logger: logging.Logger = logging.getLogger(__name__)


@api.get("models")
def get_models(request: HttpRequest) -> Response:  # noqa: ARG001
    """Get available models."""
    # Check if the request authorization header equals the API_KEY
    if request.headers.get("Authorization") != f"Bearer {os.getenv('SAIMI_API_KEY')}":
        print(request.headers.get("Authorization"))
        return Response({"detail": "Unauthorized"}, status=401)

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{BASE_URL}models"
    logger.debug(url)

    # Forward the request to OpenAI
    response = requests.get(
        url=url,
        headers=headers,
        timeout=TIMEOUT,
    )

    return Response(
        data=response.json(),
        status=response.status_code,
    )


def log_json(data: str | dict) -> None:
    """Log JSON data."""
    if isinstance(data, str):
        parsed_json = json.loads(data)
    else:
        parsed_json = data
    print(json.dumps(parsed_json, indent=4, sort_keys=True))


def get_chunk(content: str | bytes, role: str, model: str) -> bytes:
    """Return content as chunked data."""
    data = {
        "choices": [{"delta": {"content": content, "role": role}, "index": 0}],
        "created": int(time.time()),
        "model": model,
        "object": "chat.completion.chunk",
    }
    data_str = json.dumps(data).encode("utf-8")
    return b"\ndata: " + data_str + b"\n\n"


def strip_redaction_summary(text: str) -> tuple[str, str]:
    """Strip the redaction summary section from the provided text.

    Strips everything after the redaction summary.
    """
    return text.split(REDACTION_SUMMARY, 1)[0].strip(), text.split(
        REDACTION_SUMMARY, 1
    )[1].strip()


def replace_user_message_with_pseudonymized_data(
    original_data: dict, pseudonymized_content: str
) -> dict:
    """Replace the user message with the pseudonymized data.

    This function assumes that the user message is the last message in the list.
    """
    if original_data["messages"]:
        original_data["messages"][-1]["content"] = pseudonymized_content
    return original_data


def use_model(data: dict, model: str) -> dict:
    """Use the specified model to generate a response.

    This function assumes that the model is compatible with the provided data.
    """
    if "model" in data:
        data["model"] = model
    return data


def pseudonymization_wrapper(
    url: LiteralString, headers: dict[str, str], body: bytes
) -> Generator[bytes, None, None]:
    """Stream response from the API."""
    # Decode the body bytes into a JSON object
    original_data = json.loads(body.decode("utf-8"))

    data = original_data
    del data["stream"]

    user_selected_model = data.get("model", None)
    if user_selected_model is None:
        msg = "No model selected in the request data."
        raise ValueError(msg)

    # Step 1: De-id the content
    if "messages" in data:
        data["messages"] = [
            {
                "role": "system",
                "content": get_deid_prompt(),
            },
            {
                "role": "user",
                "content": original_data["messages"][-1]["content"],
            },
        ]
    data = use_model(data, DEID_MODEL)

    completion = pseudonymizer_client.chat.completions.create(
        **data, stream=True, temperature=0
    )

    deid_content_with_summary = ""

    for chunk in completion:
        if chunk and chunk.choices[0].delta.content is not None:
            deid_content_with_summary += chunk.choices[0].delta.content
            yield get_chunk(
                chunk.choices[0].delta.content or "",
                "de-id-assistant",
                f"{DEID_MODEL}-deid",
            )

    # Step 2: Get response for deid content

    if REDACTION_SUMMARY in deid_content_with_summary:
        deid_content = deid_content_with_summary.split(REDACTION_SUMMARY, 1)[0]

        # remove DEID_HEADER from the deid_content
        deid_content = deid_content.replace(DEID_HEADER, "").strip()

        # remove QUOTE from each line
        deid_content = "\n".join(
            line.replace(QUOTE, "") for line in deid_content.splitlines()
        )

        tokens = deid_content_with_summary.split(REDACTION_SUMMARY, 1)[1].strip()
    else:
        deid_content = deid_content_with_summary.strip()
        tokens = ""

    print("deid content:", deid_content)
    print("tokens:", tokens)

    if "messages" in data:
        data["messages"] = [
            {
                "role": "system",
                "content": USER_RESPONSE_PROMPT,
            },
            {"role": "user", "content": deid_content},
        ]

    data = use_model(data, user_selected_model)

    completion = real_client.chat.completions.create(**data, stream=True)
    response = ""

    yield get_chunk("# PSEUDONYMIZED RESPONSE\n\n", "header", user_selected_model)

    for chunk in completion:
        if chunk and (resp := chunk.choices[0].delta.content) is not None:
            response += resp
            yield get_chunk(resp or "", "assistant", user_selected_model)

    print("response:", response)

    # Step 3: Re-identify the response

    data = use_model(data, DEID_MODEL)

    if "messages" in data:
        data["messages"] = [
            {"role": "system", "content": f"{reid_instructions(tokens)}"},
            {"role": "user", "content": response},
        ]

    yield get_chunk(
        "\n\n---\n\n# RE-IDENTIFIED RESPONSE\n\n",
        "reid-assistant",
        f"{DEID_MODEL}-reid",
    )

    completion = pseudonymizer_client.chat.completions.create(
        **data, stream=True, temperature=0
    )
    for chunk in completion:
        if chunk and (resp := chunk.choices[0].delta.content) is not None:
            yield get_chunk(resp or "", "reid-assistant", f"{DEID_MODEL}-reid")


@api.post("chat/completions")
async def openai_proxy(request: HttpRequest) -> StreamingHttpResponse | Response:
    """Proxy requests to OpenAI API."""
    # Check if the request authorization header equals the API_KEY
    if request.headers.get("Authorization") != f"Bearer {os.getenv('SAIMI_API_KEY')}":
        # Print hash
        print(request.headers.get("Authorization"))
        return Response({"detail": "Unauthorized"}, status=401)

    # Prepare headers
    headers: dict[str, str] = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }

    url: LiteralString = f"{BASE_URL}chat/completions"

    parsed_json = json.loads(request.body)
    print(json.dumps(parsed_json, indent=4, sort_keys=True))

    # Detect if the request is a summary request i.e. having stream=false and max_tokens=1000
    if (
        parsed_json.get("stream", True) is False
        and parsed_json.get("max_tokens", 0) == 1000
    ):
        del parsed_json["stream"]
        parsed_json["model"] = SUMMARY_MODEL
        completion = real_client.chat.completions.create(**parsed_json, stream=False)
        return Response(data=completion)

    # Return a streaming response
    return StreamingHttpResponse(
        streaming_content=pseudonymization_wrapper(
            url=url, headers=headers, body=request.body
        ),
        content_type="text/event-stream",
    )

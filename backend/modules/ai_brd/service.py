import json
from openai import OpenAI
from pydantic import ValidationError
from .prompts import BRD_SCHEMA, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .schemas import BRDJson


class BRDService:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_brd(self, cleaned_transcript: str) -> dict:
        if not cleaned_transcript:
            raise ValueError("Missing cleaned transcript")
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": USER_PROMPT_TEMPLATE.format(transcript=cleaned_transcript),
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "brd",
                    "schema": BRD_SCHEMA,
                    "strict": True,
                }
            },
            temperature=0,
        )
        output_text = self._extract_output_text(response)
        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON from model: {exc}") from exc

        try:
            BRDJson(**payload)
        except ValidationError as exc:
            raise ValueError(f"BRD schema validation failed: {exc}") from exc

        return payload

    def _extract_output_text(self, response) -> str:
        if getattr(response, "output_text", None):
            return response.output_text
        output = getattr(response, "output", []) or []
        for item in output:
            content = getattr(item, "content", []) or []
            for block in content:
                if getattr(block, "type", "") == "output_text":
                    return block.text
        raise ValueError("Model response did not include output text")

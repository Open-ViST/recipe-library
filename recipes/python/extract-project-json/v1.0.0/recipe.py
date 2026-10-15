"""OpenViST recipe: extract a small record. An API call happens only when you run this file."""
from openai import OpenAI
from pydantic import BaseModel


class Project(BaseModel):
    name: str
    purpose: str
    requirements: list[str]


SOURCE = "ExampleTool formats local JSON files. It requires Python 3. Its source is https://example.org/tool."


def extract(source=SOURCE):
    client = OpenAI(timeout=30, max_retries=0)
    response = client.responses.parse(
        model="gpt-6-luna",
        reasoning={"effort": "none"},
        service_tier="default",
        max_output_tokens=500,
        input=[
            {"role": "system", "content": "Extract only facts explicitly stated. Use an empty string or list for missing facts."},
            {"role": "user", "content": source},
        ],
        text_format=Project,
    )
    if response.status != "completed" or response.output_parsed is None:
        raise RuntimeError("The model did not return a complete parsed record; inspect status and refusals.")
    return response.output_parsed


if __name__ == "__main__":
    print(extract().model_dump_json(indent=2))

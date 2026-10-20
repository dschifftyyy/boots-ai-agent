import os
import sys
import argparse
from dotenv import load_dotenv
from openai import OpenAI

from config import MAX_ITERATIONS
from call_function import available_functions, call_function
from prompts import system_prompt

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key is None:
    raise RuntimeError("OPENROUTER_API_KEY not set; check your .env file.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    for _ in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
            # Only route to models that actually support tool calling.
            extra_body={"provider": {"require_parameters": True}},
        )
        if response.usage is None:
            raise RuntimeError("API response has no usage data; the request likely failed.")

        if args.verbose:
            print("Prompt tokens:", response.usage.prompt_tokens)
            print("Response tokens:", response.usage.completion_tokens)

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            print("Final response:")
            print(message.content)
            return

        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, verbose=args.verbose)
            if not result_message.get("content"):
                raise RuntimeError(
                    f"Function call {tool_call.function.name} returned no content"
                )
            if args.verbose:
                print(f"-> {result_message['content']}")
            messages.append(result_message)

    print(f"Error: agent did not produce a final response within {MAX_ITERATIONS} iterations.")
    sys.exit(1)


if __name__ == "__main__":
    main()

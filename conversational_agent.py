import os
import json
import time
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.environ.get("GROQ_API_KEY")
BASE_URL = "https://api.groq.com/openai/v1"
LLM_MODEL = "llama-3.3-70b-versatile"

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

def get_current_weather(location):
    """Get the current weather for a location."""
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY not set"})
    url = (
        f"http://api.weatherapi.com/v1/current.json"
        f"?key={api_key}&q={location}&aqi=no"
    )
    response = requests.get(url)
    data = response.json()
    if "error" in data:
        return json.dumps({"error": data["error"]["message"]})
    weather_info = data["current"]
    return json.dumps(
        {
            "location": data["location"]["name"],
            "temperature_c": weather_info["temp_c"],
            "temperature_f": weather_info["temp_f"],
            "condition": weather_info["condition"]["text"],
            "humidity": weather_info["humidity"],
            "wind_kph": weather_info["wind_kph"],
        }
    )

def get_weather_forecast(location, days=3):
    """Get a weather forecast for a location for a specified number of days."""
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "WEATHER_API_KEY not set"})
    url = (
        f"http://api.weatherapi.com/v1/forecast.json"
        f"?key={api_key}&q={location}&days={days}&aqi=no"
    )
    response = requests.get(url)
    data = response.json()
    if "error" in data:
        return json.dumps({"error": data["error"]["message"]})
    forecast_days = data["forecast"]["forecastday"]
    forecast_data = []
    for day in forecast_days:
        forecast_data.append(
            {
                "date": day["date"],
                "max_temp_c": day["day"]["maxtemp_c"],
                "min_temp_c": day["day"]["mintemp_c"],
                "condition": day["day"]["condition"]["text"],
                "chance_of_rain": day["day"]["daily_chance_of_rain"],
            }
        )
    return json.dumps(
        {
            "location": data["location"]["name"],
            "forecast": forecast_data,
        }
    )

def calculator(expression):
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city and state, e.g., San Francisco, CA, "
                            "or a country, e.g., France"
                        ),
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": (
                "Get the weather forecast for a location for a specific "
                "number of days"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city and state, e.g., San Francisco, CA, "
                            "or a country, e.g., France"
                        ),
                    },
                    "days": {
                        "type": "integer",
                        "description": "The number of days to forecast (1-10)",
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["location"],
            },
        },
    },
]

calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "The mathematical expression to evaluate, "
                        "e.g., '2 + 2' or '5 * (3 + 2)'"
                    ),
                }
            },
            "required": ["expression"],
        },
    },
}

cot_tools = weather_tools + [calculator_tool]
available_functions = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
    "calculator": calculator,
}

cot_system_message = """You are a helpful assistant that can answer questions
about weather and perform calculations.
When responding to complex questions, please follow these steps:
1. Think step-by-step about what information you need.
2. Break down the problem into smaller parts.
3. Use the appropriate tools to gather information.
4. Explain your reasoning clearly.
5. Provide a clear final answer.
For example, if someone asks about temperature conversions or
comparisons between cities, first get the weather data, then use the
calculator if needed, showing your work.
"""

advanced_system_message = """You are a helpful weather assistant that can use
weather tools and a calculator to solve multi-step problems.
Guidelines:
1. If the user asks about several independent locations, use multiple weather
tool calls in parallel when appropriate.
2. If a question requires several steps, continue using tools until the task is
completed.
3. If a tool fails, explain the issue clearly and continue safely when possible.
4. For complex comparison or calculation queries, prepare a structured final
response.
"""

def process_messages(client, messages, tools=None, available_functions=None):
    """Process messages and invoke tools as needed."""
    tools = tools or []
    available_functions = available_functions or {}

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=tools,
    )
    response_message = response.choices[0].message
    messages.append(response_message)

    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

    return messages

def run_conversation(client, system_message="You are a helpful weather assistant."):
    """Run a conversation with the user, processing their messages and handling tool calls."""
    messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]
    print("Weather Assistant: Hello! I can help you with weather information.")
    print("Ask me about the weather anywhere!")
    print("(Type 'exit' to end the conversation)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nWeather Assistant: Goodbye! Have a great day!")
            break
        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        messages = process_messages(
            client,
            messages,
            weather_tools,
            available_functions,
        )

        last_message = messages[-1]
        if last_message["role"] == "assistant" and last_message.get("content"):
            print(f"\nWeather Assistant: {last_message['content']}\n")

    return messages

def execute_tool_safely(tool_call, available_functions):
    """Execute a tool call with validation and error handling."""
    function_name = tool_call.function.name
    if function_name not in available_functions:
        return json.dumps(
            {
                "success": False,
                "error": f"Unknown function: {function_name}",
            }
        )
    try:
        function_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Invalid JSON arguments: {str(e)}",
            }
        )
    try:
        function_response = available_functions[function_name](**function_args)
        return json.dumps(
            {
                "success": True,
                "function_name": function_name,
                "result": function_response,
            }
        )
    except TypeError as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Invalid arguments: {str(e)}",
            }
        )
    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
            }
        )

def execute_tools_sequential(tool_calls, available_functions):
    """Execute tool calls one after another."""
    results = []
    for tool_call in tool_calls:
        safe_result = execute_tool_safely(tool_call, available_functions)
        tool_message = {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_call.function.name,
            "content": safe_result,
        }
        results.append(tool_message)
    return results

def execute_tools_parallel(tool_calls, available_functions, max_workers=4):
    """Execute independent tool calls in parallel."""
    def run_single_tool(tool_call):
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_call.function.name,
            "content": execute_tool_safely(tool_call, available_functions),
        }
    with ThreadPoolExecutor(
        max_workers=min(max_workers, len(tool_calls))
    ) as executor:
        return list(executor.map(run_single_tool, tool_calls))

def compare_parallel_vs_sequential(tool_calls, available_functions):
    """Measure the timing difference between sequential and parallel execution."""
    start = time.perf_counter()
    sequential_results = execute_tools_sequential(tool_calls, available_functions)
    sequential_time = time.perf_counter() - start

    start = time.perf_counter()
    parallel_results = execute_tools_parallel(tool_calls, available_functions)
    parallel_time = time.perf_counter() - start

    speedup = (
        sequential_time / parallel_time if parallel_time > 0 else None
    )

    return {
        "sequential_results": sequential_results,
        "parallel_results": parallel_results,
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "speedup": speedup,
    }

def process_messages_advanced(client, messages, tools=None, available_functions=None):
    """Send messages to the model and execute any returned tools in parallel."""
    tools = tools or []
    available_functions = available_functions or {}

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=tools,
    )
    response_message = response.choices[0].message
    messages.append(response_message)

    if response_message.tool_calls:
        tool_results = execute_tools_parallel(
            response_message.tool_calls,
            available_functions,
        )
        messages.extend(tool_results)

    return messages, response_message

def run_conversation_advanced(
    client,
    system_message=advanced_system_message,
    max_iterations=5,
):
    """Run a conversation that supports multi-step tool workflows."""
    messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]
    print("Advanced Weather Assistant: Hello! Ask me complex weather questions.")
    print("I can compare cities, perform calculations, and return structured outputs.")
    print("(Type 'exit' to end the conversation)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nAdvanced Weather Assistant: Goodbye! Have a great day!")
            break
        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        for _ in range(max_iterations):
            messages, response_message = process_messages_advanced(
                client, messages, cot_tools, available_functions
            )

            if not response_message.tool_calls:
                last_message = messages[-1]
                if last_message.get("content"):
                    print(f"\nAdvanced Weather Assistant: {last_message['content']}\n")
                break
        else:
            print(
                "\nAdvanced Weather Assistant: I stopped after reaching the"
                " maximum number of tool iterations.\n"
            )

    return messages

required_output_keys = [
    "query_type",
    "locations",
    "summary",
    "tool_calls_used",
    "final_answer",
]

structured_output_prompt = """For complex comparison or calculation queries,
return the final answer as a valid JSON object with exactly these keys:
- query_type
- locations
- summary
- tool_calls_used
- final_answer
Do not include markdown fences.
"""

def validate_structured_output(response_text):
    """Validate the final structured JSON response."""
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON output: {str(e)}")
    for key in required_output_keys:
        if key not in parsed:
            raise ValueError(f"Missing required key: {key}")
    if not isinstance(parsed["locations"], list):
        raise ValueError("'locations' must be a list")
    if not isinstance(parsed["tool_calls_used"], list):
        raise ValueError("'tool_calls_used' must be a list")
    return parsed

def get_structured_final_response(client, messages):
    """Request a structured final response in JSON mode and validate it."""
    structured_messages = messages + [
        {
            "role": "system",
            "content": structured_output_prompt,
        }
    ]
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=structured_messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    validated = validate_structured_output(content)
    return validated

def run_comparative_evaluation(client, query):
    """Run all three agent types and compare results."""
    print("=" * 60)
    print("COMPARATIVE EVALUATION")
    print("=" * 60)
    print(f"\nQuery: {query}\n")

    messages_basic = [{"role": "system", "content": "You are a helpful weather assistant."}]
    messages_cot = [{"role": "system", "content": cot_system_message}]
    messages_advanced = [{"role": "system", "content": advanced_system_message}]

    messages_basic.append({"role": "user", "content": query})
    messages_cot.append({"role": "user", "content": query})
    messages_advanced.append({"role": "user", "content": query})

    def get_response_content(msg):
        if isinstance(msg, dict):
            return msg.get("content")
        return getattr(msg, "content", None)

    print("Running Basic Agent...")
    messages_basic = process_messages(client, messages_basic, weather_tools, available_functions)
    basic_response = get_response_content(messages_basic[-1]) or "No response"

    print("Running Chain of Thought Agent...")
    messages_cot = process_messages(client, messages_cot, cot_tools, available_functions)
    cot_response = get_response_content(messages_cot[-1]) or "No response"

    print("Running Advanced Agent...")
    messages_advanced, _ = process_messages_advanced(client, messages_advanced, cot_tools, available_functions)
    advanced_response = get_response_content(messages_advanced[-1]) or "No response"

    print("\n" + "-" * 60)
    print("RESULTS")
    print("-" * 60)
    print(f"\n[Basic Agent]:\n{basic_response}\n")
    print(f"[Chain of Thought Agent]:\n{cot_response}\n")
    print(f"[Advanced Agent]:\n{advanced_response}\n")

    print("-" * 60)
    print("RATING (1-5 for each agent)")
    print("-" * 60)
    try:
        basic_rating = int(input("Rate Basic Agent (1-5): ") or 3)
        cot_rating = int(input("Rate CoT Agent (1-5): ") or 3)
        advanced_rating = int(input("Rate Advanced Agent (1-5): ") or 3)
    except ValueError:
        basic_rating, cot_rating, advanced_rating = 3, 3, 3

    results = {
        "query": query,
        "basic_response": basic_response,
        "cot_response": cot_response,
        "advanced_response": advanced_response,
        "basic_rating": basic_rating,
        "cot_rating": cot_rating,
        "advanced_rating": advanced_rating,
    }

    save_results_to_csv(results)

    return results

def save_results_to_csv(results):
    """Save evaluation results to CSV."""
    import csv
    csv_file = "evaluation_results.csv"
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(results)
    print(f"\nResults saved to {csv_file}")

if __name__ == "__main__":
    print("Weather Assistant - CSAI 422 Assignment 3")
    print("=" * 50)
    choice = input(
        "\nChoose an agent type:\n1: Basic\n2: Chain of Thought\n3: Advanced\n4: Comparative Evaluation\nChoice: "
    )
    
    if choice == "1":
        run_conversation(client, "You are a helpful weather assistant.")
    elif choice == "2":
        run_conversation(client, cot_system_message)
    elif choice == "3":
        run_conversation_advanced(client, advanced_system_message)
    elif choice == "4":
        query = input("Enter a multi-location query (e.g., 'Compare weather in Cairo, London, and Paris'): ")
        if query:
            run_comparative_evaluation(client, query)
        else:
            run_comparative_evaluation(client, "Compare the weather in Cairo, London, and Paris")
    else:
        print("Invalid choice. Defaulting to Basic agent.")
        run_conversation(client, "You are a helpful weather assistant.")

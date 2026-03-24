# Weather Assistant - CSAI 422 Assignment 3

A conversational weather assistant with tool use and reasoning techniques, built with the Groq API.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Groq API key
- WeatherAPI key (free tier available at [weatherapi.com](https://www.weatherapi.com/))

### 2. Installation

```bash
pip install openai python-dotenv requests
```

### 3. Configuration

Create a `.env` file in the project root:

```
WEATHER_API_KEY=your_weatherapi_key_here
```

The Groq API key is already configured in the script. To use your own, set:
```
GROQ_API_KEY=your_groq_key_here
```

### 4. Running the Application

```bash
python conversational_agent.py
```

Choose an agent type when prompted:
- **1**: Basic Agent - Simple weather queries
- **2**: Chain of Thought Agent - Step-by-step reasoning
- **3**: Advanced Agent - Parallel execution and structured outputs
- **4**: Comparative Evaluation - Compare all three agents

---

## Implementation Documentation

### Part 1: Basic Tool Calling
The Basic Agent implements weather tool definitions using OpenAI's function calling format:
- `get_current_weather`: Fetches current weather for a location
- `get_weather_forecast`: Gets weather forecast for 1-10 days

The `process_messages` function handles the tool-calling loop: sends messages to the model, receives tool calls, executes them, and appends results back to the conversation.

### Part 2: Chain of Thought Reasoning
Enhanced with:
- Calculator tool for mathematical operations
- CoT system message prompting step-by-step reasoning
- The agent explains its thinking process before providing answers

### Part 3: Advanced Tool Orchestration
- **Parallel Execution**: Uses `ThreadPoolExecutor` to execute independent tool calls concurrently
- **Safe Tool Execution**: `execute_tool_safely` validates tool names and JSON arguments, returns structured success/error results
- **Multi-Step Workflows**: `process_messages_advanced` supports multiple iteration rounds of tool use
- **Structured Outputs**: Validates JSON responses against required schema keys

### Bonus: Comparative Evaluation
- Runs the same query through all three agent types
- Measures execution time for parallel vs sequential tool calls
- Collects user ratings and saves results to CSV

---

## Example Conversations

### Basic Agent
```
Weather Assistant: Hello! I can help you with weather information.
Ask me about the weather anywhere!
(Type 'exit' to end the conversation)

You: What's the weather in Cairo?
Weather Assistant: Currently in Cairo, it's sunny with a temperature of 28°C (82°F). 
The humidity is at 45% and wind speed is 15 km/h.

You: exit
```

### Chain of Thought Agent
```
You: What's the temperature difference between Cairo and London?

Weather Assistant: Let me work through this step-by-step:

1. First, I need to get the current temperature in both Cairo and London.
2. I'll call the weather tool for both cities.
3. Once I have the data, I'll use the calculator to find the difference.

Results:
- Cairo: 28°C
- London: 15°C

Temperature difference: 13°C

Cairo is 13 degrees warmer than London right now.
```

### Advanced Agent
```
Advanced Weather Assistant: Hello! Ask me complex weather questions.
I can compare cities, perform calculations, and return structured outputs.

You: Compare weather in Cairo, London, and Paris

Advanced Weather Assistant: Here's the comparison:

| City   | Temp (°C) | Condition  | Humidity |
|--------|-----------|-------------|----------|
| Cairo  | 28        | Sunny       | 45%      |
| London | 15        | Cloudy      | 70%      |
| Paris  | 18        | Partly Cloudy | 60%   |

Warmest: Cairo (28°C)
Coolest: London (15°C)

Tool calls used: get_current_weather (3x parallel)
```

---

## Analysis: Reasoning and Orchestration Strategies

### Basic Agent
- **Quality**: Simple, direct responses suitable for single-location queries
- **Performance**: Fast for single queries, sequential tool execution
- **Best for**: Quick, straightforward weather lookups

### Chain of Thought Agent
- **Quality**: Higher quality for complex queries - explains reasoning, shows work
- **Performance**: Similar to basic for single tool calls, adds minimal overhead
- **Best for**: Queries requiring calculations or comparisons
- **Improvement**: More transparent reasoning helps users understand the answer

### Advanced Agent
- **Quality**: Best for multi-location queries with structured, comprehensive answers
- **Performance**: Parallel execution provides significant speedup for independent calls
- **Best for**: Complex multi-step workflows, comparisons across many cities

### Parallel vs Sequential Execution
When querying 3+ independent locations:
- **Sequential**: ~3 seconds (1 second per call)
- **Parallel**: ~1 second (all calls simultaneously)
- **Speedup**: ~3x improvement

Parallel execution is most beneficial when:
- Multiple independent API calls are needed
- Network latency dominates processing time
- Calls don't depend on each other's results

Multi-step reasoning remains necessary even with parallel execution when:
- Later steps depend on earlier results
- Conditional logic requires checking intermediate values
- Complex aggregations need multiple data sources

---

## Challenges and Solutions

### 1. API Key Configuration
**Challenge**: Environment variables not loading correctly.
**Solution**: Used `python-dotenv` with explicit `.env` file loading and fallback defaults in code.

### 2. Tool Response Handling
**Challenge**: Response objects from OpenAI vary in type (some dicts, some objects).
**Solution**: Created helper function `get_response_content()` to handle both types safely.

### 3. Parallel Execution Timing
**Challenge**: Measuring accurate timing differences between sequential and parallel execution.
**Solution**: Used `time.perf_counter()` for high-resolution timing and proper iteration.

### 4. Structured Output Validation
**Challenge**: Ensuring JSON output from LLM matches required schema.
**Solution**: Implemented `validate_structured_output()` with checks for all required keys and types.

### 5. Groq API Compatibility
**Challenge**: Switching from OpenAI to Groq required different base URL configuration.
**Solution**: Configured OpenAI client with Groq's base URL (`https://api.groq.com/openai/v1`).

---

## File Structure

```
Applied_Assi_3/
├── conversational_agent.py   # Main application code
├── .env                       # Environment variables (API keys)
├── README.md                  # This file
├── evaluation_results.csv     # Saved comparative evaluation results (generated)
└── venv/                      # Virtual environment
```

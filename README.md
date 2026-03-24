Weather Assistant - CSAI 422 Assignment 3

Overview
In this assignment I created a conversational weather assistant that can answer questions using external tools. The assistant can get real-time weather data, do calculations, and handle more complex questions step by step.

The purpose of this work was to understand how tool calling works and how an AI system can solve problems in multiple steps instead of giving direct answers only.

Setup Instructions

Requirements
Python 3.8 or higher
Groq API key
Weather API key

Installation
Install the required libraries:
pip install openai python-dotenv requests

Configuration
Create a file called .env in the same folder and add:
GROQ_API_KEY=your_key_here
WEATHER_API_KEY=your_key_here

The .env file is not uploaded to GitHub to keep the keys safe.

How to Run
Run the program using:
python conversational_agent.py

Then choose one of the options:
1 Basic Agent
2 Chain of Thought Agent
3 Advanced Agent
4 Comparative Evaluation

Implementation

Part 1 Basic Tool Calling
I created two main functions, one for current weather and one for forecast. The assistant uses these functions when needed and returns the result to the user.

Part 2 Chain of Thought
I added a calculator and made the assistant explain its steps when answering more complex questions. This made the answers clearer and easier to follow.

Part 3 Advanced Agent
In this part I added parallel execution, safe tool handling, and multi-step workflows. The assistant can continue working until it reaches the final answer.

Example Usage

Basic
User asks about weather in a city and the assistant returns the current conditions.

Chain of Thought
User asks for comparison between cities and the assistant explains the steps and calculates the result.

Advanced
User asks about multiple cities and the assistant compares them using multiple tool calls.

Analysis
The basic version is simple and fast but limited.
The chain of thought version is clearer because it explains the reasoning.
The advanced version handles more complex questions and works better for multiple cities.

Parallel execution improves performance when more than one request is needed.

Challenges
At first I had issues with API keys and accidentally exposed one, but I fixed it by using a .env file and removing it from the repository.

Another issue was making sure tool calls worked correctly in different modes, which I solved by organizing the code into helper functions.

What I Learned
I learned how AI models can use external tools, how reasoning improves answers, and how to handle multi-step tasks. I also understood when parallel execution is useful.

File Structure
CSAI422_Assignment3
conversational_agent.py
README.md
.env.example

Final Note
This assignment helped me understand how AI systems can interact with real data and solve problems step by step.

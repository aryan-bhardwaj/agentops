import os
from dotenv import load_dotenv
import agentops
import asyncio
from agents import Runner, Agent, function_tool

# Load environment variables from .env file
load_dotenv()
# Get API key from environment variables
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
# Initialize AgentOps - this is all you need for automatic instrumentation
agentops.init(api_key=AGENTOPS_API_KEY, default_tags=["wellness_coach"])


@function_tool
def web_search(query: str) -> str:
    """
    Search the web for information.
    
    Args:
        query: The search query
    
    Returns:
        Search results from the web
    """
    # Use OpenAI's built-in web search
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        tools=[{"type": "web_search"}]
    )
    
    # Extract the search results from the response
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        search_results = tool_calls[0].function.arguments
        return f"Web search results for: {query}\n\n{search_results}"
    else:
        return f"No search results found for: {query}"

nutrition_agent = Agent(
    name="nutrition_agent",
    instructions="""You are a nutrition specialist.
    
    When asked about food or meals, use the web_search tool to find nutritional information.
    Return the information in a clear, structured format.
    
    Always include:
    - Identified foods
    - Estimated calories (when possible)
    - Nutritional recommendations
    
    After providing your recommendations, ask ONE specific follow-up question to learn more about the user's 
    dietary preferences, restrictions, or habits. This will help you provide more personalized nutrition advice.
    """,
    tools=[web_search]
)

workout_agent = Agent(
    name="workout_agent",
    instructions="""You are a fitness trainer.
    
    When asked about workouts or exercises, use the web_search tool to find appropriate workout plans.
    Consider the user's fitness level, available equipment, and goals.
    
    Always include:
    - List of recommended exercises
    - Recommended duration
    - Intensity level
    
    After providing your workout recommendations, ask ONE specific follow-up question to learn more about the 
    user's fitness level, available equipment, or exercise preferences. This will help you tailor future workout suggestions.
    """,
    tools=[web_search]
)

bmi_agent = Agent(
    name="bmi_agent",
    instructions="""You are a BMI calculator and advisor.
    
    Calculate BMI using the formula: weight(kg) / height(m)².
    Provide the BMI category and appropriate health advice.
    Use web_search to find additional information if needed.
    
    After providing BMI information, ask ONE specific follow-up question about the user's health goals or 
    current lifestyle to help provide more personalized health recommendations.
    """,
    tools=[web_search]
)

sleep_agent = Agent(
    name="sleep_agent",
    instructions="""You are a sleep specialist.
    
    Provide sleep recommendations based on the user's wake-up time and sleep needs.
    Use web_search to find sleep hygiene tips and other relevant information.
    
    After providing sleep advice, ask ONE specific follow-up question about the user's current sleep habits, 
    bedtime routine, or sleep environment to help provide more tailored recommendations.
    """,
    tools=[web_search]
)

health_coach = Agent(
    name="health_coach",
    instructions="""You are a helpful health and wellness coach.

    Your job is to help users improve their physical health, nutrition, sleep, and overall wellness.
    
    For nutrition questions, hand off to the nutrition_agent.
    For workout questions, hand off to the workout_agent.
    For BMI calculations, hand off to the bmi_agent.
    For sleep recommendations, hand off to the sleep_agent.
    
    For general health questions, use web_search to find relevant information.
    
    IMPORTANT: Always personalize your advice. After answering a user's question, ask ONE specific follow-up 
    question to learn more about their personal situation, preferences, or health metrics. This will help you 
    provide more tailored recommendations in future interactions.
    
    Examples of good follow-up questions:
    - "What foods do you typically enjoy for breakfast?"
    - "How much time can you realistically dedicate to exercise each day?"
    - "Do you have any dietary restrictions I should be aware of?"
    - "What time do you usually wake up in the morning?"
    
    Be supportive, encouraging, and non-judgmental. Focus on sustainable habits rather than quick fixes.
    """,
    tools=[web_search],
    handoffs=[nutrition_agent, workout_agent, bmi_agent, sleep_agent]
)

async def main():
    print("Welcome to the Health and Wellness Coach!")
    print("I can help you with workouts, nutrition, sleep, and general wellness advice.")
    print("Type 'exit' at any time to end the conversation.\n")
    
    query = input("How can I help with your health and wellness goals today? ")
    
    while query.lower() != 'exit':
        try:
            # Run the agent - AgentOps will automatically track this
            result = await Runner.run(health_coach, query)
            
            # Print the response to the user
            print(f"\nHealth Coach: {result.final_output}\n")
            
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}\n")
        
        # Get the next query
        query = input("You: ")
if __name__ == "__main__":
    asyncio.run(main())
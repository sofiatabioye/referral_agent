# from smolagents import (
#     CodeAgent,
#     ToolCallingAgent,
#     HfApiModel,
#     ManagedAgent,
#     DuckDuckGoSearchTool,
#     LiteLLMModel,
# )

# model = HfApiModel(model_id)

# web_agent = ToolCallingAgent(
#     tools=[DuckDuckGoSearchTool(), visit_webpage],
#     model=model,
#     max_steps=10,
# )

# managed_web_agent = ManagedAgent(
#     agent=web_agent,
#     name="search",
#     description="Runs web searches for you. Give it your query as an argument.",
# )

# manager_agent = CodeAgent(
#     tools=[],
#     model=model,
#     managed_agents=[managed_web_agent],
#     additional_authorized_imports=["time", "numpy", "pandas"],
# )

# answer = manager_agent.run("If LLM training continues to scale up at the current rhythm until 2030, what would be the electric power in GW required to power the biggest training runs by 2030? What would that correspond to, compared to some countries? Please provide a source for any numbers used.")

from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel  
  
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=HfApiModel())  
  
agent.run("How many seconds would it take for a leopard at full speed to run across the Pont des Arts?")
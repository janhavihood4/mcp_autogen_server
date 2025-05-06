import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
 
# Ensure parent directory for imports (if needed)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
 
sys.path.insert(0, parent_dir)
load_dotenv()
    # Custom logger setup
from logger_utility import setup_logger
logger = setup_logger()
   
    # Autogen and MCP imports
from autogen_ext.models.openai import OpenAIChatCompletionClient
#from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools, SseServerParams
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core import CancellationToken
from autogen_core.models import UserMessage
from autogen_agentchat.base import Handoff
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
   
async def main() -> None:
    logger.info("Starting Autogen MCP client main()")
 
    key = os.getenv("GEMINI_API_KEY")  # Note the quotes around the key name
    if not key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    logger.debug("Environment variables loaded")
 
    # Specify the command and arguments to start your Microsoft API MCP server.
    # server_params = StdioServerParams(
    #     command="python",
    #     args=[
    #         "weather.py"
    #     ],
    # )
    server_params = SseServerParams(
        url="http://127.0.0.1:8000/sse",  # Correct endpoint path
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    logger.debug(f"Server params: {server_params}")
 
    # Retrieve available tools from the server.
    try:
        tools = await mcp_server_tools(server_params)
        logger.info(f"Retrieved {len(tools)} tools from MCP server")
    except Exception as e:
        logger.error(f"Failed to retrieve MCP tools: {e}")
        return
    print("Available tools:", tools)
 
 
    anthropic_client = OpenAIChatCompletionClient(
        model="gemini-1.5-pro",
        api_key= key
    )
 
    # Create a model client using Anthropic
    # anthropic_client = AnthropicChatCompletionClient(
    #     model="claude-3-7-sonnet-20250219",
    #     api_key="",
    # )
    logger.info("Anthropic client initialized")
 
    # Set up agents
    user = UserProxyAgent("user", input_func=input)
    agent = AssistantAgent(
        name="Weather_agent",
        model_client=anthropic_client,
        tools=tools,
        handoffs=[Handoff(target="user", message="Transfer to user.")],
        reflect_on_tool_use=False,
    )
    logger.info("AssistantAgent and UserProxyAgent created")
 
    # Termination conditions
    handoff_termination = HandoffTermination(target="user")
    text_termination = TextMentionTermination("TERMINATE")
 
    team = RoundRobinGroupChat(
        [agent, user],
        termination_condition=handoff_termination | text_termination
    )
    logger.info("RoundRobinGroupChat configured")
 
    task = "Whats the weather of Texas?"
    logger.info(f"Starting console run with task: {task}")
 
    try:
        await Console(team.run_stream(task=task))
        logger.info("Console run completed successfully")
    except Exception as e:
        logger.error(f"Error during console run: {e}")
 
if __name__ == "__main__":
    try:
        print("SERVER STARTED !!!!")
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Fatal error in main: {e}")
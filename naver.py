import getpass
import os
from langchain_naver_community.utils import NaverSearchAPIWrapper
from langchain_naver_community.tool import NaverSearchResults, NaverNewsSearch
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



if not os.environ.get("NAVER_CLIENT_ID"):
    os.environ["NAVER_CLIENT_ID"] = getpass.getpass("Enter your Naver Client ID:\n")

if not os.environ.get("NAVER_CLIENT_SECRET"):
    os.environ["NAVER_CLIENT_SECRET"] = getpass.getpass(
        "Enter your Naver Client Secret:\n"
    )
    

search = NaverSearchAPIWrapper()

tool = NaverSearchResults(api_wrapper=search)

# data = tool.invoke("서울 오늘 현재 날씨 기온")[0:5]
# print(data)



tools = [tool]

llm = ChatOpenAI(model="gpt-4.1-nano", api_key=os.environ.get("OPENAI_API_KEY"))
system_prompt = """
You are a helpful assistant that can search the web for information.
"""

agent_executor = create_react_agent(
    llm,
    tools,
    prompt=system_prompt,
)





query = "서울 오늘 현재 날씨 기온"
result = agent_executor.invoke({"messages": [("human", query)]})
data = result["messages"][-1].content
print(data)


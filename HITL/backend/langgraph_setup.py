from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from typing import List, Dict
from urllib.parse import quote
import feedparser

class GoogleNews:
    def __init__(self):
        self.base_url = "https://news.google.com/rss"

    def _fetch_news(self, url: str, k: int = 3) -> List[Dict[str, str]]:
        news_data = feedparser.parse(url)
        return [{"title": entry.title, "link": entry.link} for entry in news_data.entries[:k]]

    def _collect_news(self, news_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return [{"url": news["link"], "content": news["title"]} for news in news_list]

    def search_by_keyword(self, keyword: str = None, k: int = 3) -> List[Dict[str, str]]:
        if keyword:
            encoded = quote(keyword)
            url = f"{self.base_url}/search?q={encoded}&hl=en&gl=US&ceid=US:en"
        else:
            url = f"{self.base_url}?hl=en&gl=US&ceid=US:en"
        news_list = self._fetch_news(url, k)
        return self._collect_news(news_list)


class State(TypedDict):
    messages: list

graph_builder = StateGraph(State)

@tool
def search_keyword(query: str) -> List[Dict[str, str]]:
    """Look up news articles by a given keyword using Google News RSS feed."""
    news_tool = GoogleNews()
    return news_tool.search_by_keyword(query, k=5)

tools = [search_keyword]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

def chatbot_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot_node)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

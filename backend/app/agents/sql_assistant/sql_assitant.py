from app.agents.graphs import MessagesStateType
from app.agents.graphs.tool_node import MessagesBasedToolNode, route_tools
from langchain.prompts import ChatPromptTemplate
from langchain_community.agent_toolkits.sql.prompt import SQL_PREFIX
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from langchain_core.language_models import BaseChatModel
from langgraph.constants import START
from langgraph.graph import StateGraph


class SQLAssistant:
    _db: SQLDatabase
    _model: BaseChatModel

    def __init__(self, db: SQLDatabase, model: BaseChatModel):
        self._db = db
        self._model = model
        self._toolkit = SQLDatabaseToolkit(db=db, llm=self._model)
        self._tools = self._toolkit.get_tools()

    def create_bot(self):
        return ChatPromptTemplate.from_messages([
            ("system", SQL_PREFIX.format(dialect=self._db.dialect, top_k=10)),
            ("placeholder", "{messages}"),
        ]) | self._model.bind_tools(self._tools)

    def basic_graph_builder(self):
        graph_builder = StateGraph(MessagesStateType)
        tool_node = MessagesBasedToolNode(tools=self._tools)
        chatbot_runnable = self.create_bot()

        def chatbot(state):
            return {"messages": [chatbot_runnable.invoke(state)]}

        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges(
            "chatbot",
            route_tools,
            {"tools": "tools", "__end__": "__end__"},
        )
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        return graph_builder

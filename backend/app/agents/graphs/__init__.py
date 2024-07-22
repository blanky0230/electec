from typing import Annotated, TypedDict

from langchain.schema import BaseMessage
from langgraph.graph import add_messages


MessagesStateType = TypedDict(
    "MessagesStateType", {"messages": Annotated[list[BaseMessage], add_messages]}
)
ListStateType = Annotated[list[BaseMessage], add_messages]
StateType = MessagesStateType | ListStateType

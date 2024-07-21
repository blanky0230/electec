from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///elec_tec_ecommerce.db")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools")

antwort = agent_executor.invoke(
    {
        "input": "Fetch the oldest unresolved ticket from the Support tickets table. Then draft an email to the customer with a proposed solution."
    },
)


from typing import Any, TypedDict, cast
from app.agents.sql_assistant.sql_assitant import SQLAssistant
from langchain.schema import HumanMessage
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langsmith import Client, EvaluationResult, evaluate
from langsmith.schemas import Example, Run


client = Client()
model_name = "gpt-3.5-turbo"

dataset_name = "sql_assistant_calls_tools"
experiment_prefix = f"sql-agent-{model_name}".format(model_name=model_name)
metadata = "ElecTec, {model_name}, sql-assistant-base".format(model_name=model_name)

if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(
        dataset_name, description="First Tool call is 'sql_db_list_tables'"
    )
    examples = [
        ("List all Tables", "sql_db_list_tables"),
        ("Get the latest Tickets", "sql_db_list_tables"),
        ("Where can I find Support-Tickets?", "sql_db_list_tables"),
        ("What data is available to you?", "sql_db_list_tables"),
        ("What table stores shipping information?", "sql_db_list_tables"),
    ]

    inputs, outputs = zip(*[
        ({"input": _in}, {"first_tool": _exp}) for _in, _exp in examples
    ])

    client.create_examples(
        dataset_id=dataset.id,
        inputs=inputs,
        outputs=outputs,
    )
else:
    dataset = client.read_dataset(dataset_name=dataset_name)

assistant_runnable = (
    SQLAssistant(
        SQLDatabase.from_uri("sqlite:///elec_tec_ecommerce.db"),
        ChatOpenAI(model=model_name, temperature=0),
    )
    .basic_graph_builder()
    .compile()
)


class ExperimentInputType(TypedDict):
    input: str
    expect: str


def predict_assistant(experiment_input: dict[Any, Any] | ExperimentInputType) -> dict:
    """Invoke assistant for single tool call evaluation"""
    msg = {"messages": [HumanMessage(content=experiment_input["input"])]}
    result = assistant_runnable.invoke(msg)
    return {"response": result}


def check_first_tool_call(root_run: Run, example: Example | None) -> EvaluationResult:
    """
    Check if the first tool call in the response matches the expected tool call.
    """
    assert example is not None and example.outputs is not None
    assert root_run.outputs is not None

    expected_tool_call = example.outputs["first_tool"]  # "sql_db_list_tables"

    tool_calls = _find_tool_calls(root_run.outputs["response"])

    try:
        tool_call = tool_calls[0]
    except IndexError:
        tool_call = None

    score = 1 if tool_call == expected_tool_call else 0
    return cast(EvaluationResult, {"score": score, "key": "first_tool_lists_tables"})


def _find_tool_calls(state: dict):
    """
    Find all tool calls in the messages returned
    """
    tool_calls = [
        tc["name"] for m in state["messages"] for tc in getattr(m, "tool_calls", [])
    ]
    return tool_calls


def check_tool_call_contains(root_run: Run, example: Example | None):
    assert example is not None and example.outputs is not None
    assert root_run.outputs is not None
    expected_tool_call = example.outputs["first_tool"]  # "sql_db_list_tables"

    state = root_run.outputs["response"]
    tool_calls = _find_tool_calls(state)
    if any(tc == expected_tool_call for tc in tool_calls):
        score = 1
    else:
        score = 0
    return {"score": int(score), "key": "tool_call_contains"}


experiment_results = evaluate(
    predict_assistant,
    data=dataset_name,
    evaluators=[check_first_tool_call, check_tool_call_contains],
    experiment_prefix=experiment_prefix + "-first-tool",
    num_repetitions=1,
    metadata={"version": metadata},
)

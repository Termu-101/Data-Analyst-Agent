import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from utils import get_dataframe_schema
import os
import traceback
from dotenv import load_dotenv

load_dotenv()

print("API KEY: ", os.getenv("GROQ_API_KEY"))

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# api_key = os.getenv("GROQ_API_KEY")

# if not api_key:
#     raise ValueError("GROQ_API_KEY is not set in environment variables")

# client = Groq(api_key=api_key)



def suggest_insights(df: pd.DataFrame) -> str:

    schema = get_dataframe_schema(df)

    prompt = f"""You are an expert data scientist. A user just uploaded a dataset.
            Here is the dataset schema and a sample:

            {schema}

            Your job:
            1. Suggest 5 specific, interesting insights or patterns to explore in this data.
            2. Suggest 3 questions the user could ask about this data.
            3. Flag any data quality issues you notice (nulls, suspicious values, skewed distributions).

            Be specific — mention actual column names. Be concise. Use bullet points.
            Do not say "I cannot analyze" — work with what you have."""


    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=800
    )
    return response.choices[0].message.content


def answer_question(df: pd.DataFrame, question: str, chat_history: list) -> str:
    """
    Takes a user question in plain English, converts it to pandas code,
    runs that code on the real dataframe, and returns the result.
    
    chat_history is a list of past (question, answer) tuples for context.
    """
    schema = get_dataframe_schema(df)

    # Build the conversation history for the LLM
    # This lets it remember previous questions in the same session
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert data analyst. You have access to a pandas DataFrame called `df`.

            Dataset info:
            {schema}

            Rules you MUST follow:
            1. Always respond with valid Python code that operates on `df`
            2. Wrap your code in ```python ... ``` code blocks
            3. The last line of your code must assign the result to a variable called `result`
            4. `result` should be something printable: a number, string, DataFrame, or Series
            5. For charts, assign a plotly figure to `result`
            6. Keep code simple and correct
            7. If the question cannot be answered from the data, set result = "This information is not available in the dataset."

            Example:
            User: what is the average age?
            ````python
            result = df['age'].mean()
            ```"""
        }
    ]

    # Add conversation history so the LLM has context
    for past_q, past_a in chat_history[-4:]:  # last 4 exchanges only
        messages.append({"role": "user", "content": past_q})
        messages.append({"role": "assistant", "content": past_a})

    messages.append({"role": "user", "content": question})

    # Get code from LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,   # very low — we want precise code, not creativity
        max_tokens=600
    )

    llm_response = response.choices[0].message.content

    # Extract the Python code from the response
    code = extract_code(llm_response)

    if not code:
        return "I couldn't generate code for that question. Try rephrasing it."

    # Run the code on the actual dataframe
    result_text, chart = execute_code(df, code)
    return result_text, chart


def extract_code(llm_response: str) -> str:
    import re
    pattern = r"```python\s*(.*?)\s*```"
    matches = re.findall(pattern, llm_response, re.DOTALL)
    if matches:
        return matches[0]
    return llm_response.strip()       # Fallback: if no code block found, return the whole response



def execute_code(df: pd.DataFrame, code: str) -> tuple[str, object]:
    
    import plotly.graph_objects as go

    local_vars = {"df": df, "pd": pd}

    try:
        # Import plotly inside the execution context too
        exec("import plotly.express as px\nimport plotly.graph_objects as go\n" + code, local_vars)

        result = local_vars.get("result", "Code ran but no result was assigned.")

        # Check if result is a plotly figure
        if isinstance(result, go.Figure):
            return "Here's the chart:", result

        # If it's a DataFrame, show it nicely
        if isinstance(result, pd.DataFrame):
            if result.empty:
                return "The query returned an empty result.", None
            return result.to_markdown(), None

        # If it's a Series
        if isinstance(result, pd.Series):
            return result.to_string(), None

        # Otherwise just convert to string
        return str(result), None

    except Exception as e:
        # If code fails, tell the user clearly
        error_msg = f"Could not execute the query.\nError: {str(e)}\n\nTry rephrasing your question."
        return error_msg, None





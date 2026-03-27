import gradio as gr
import pandas as pd
from analyzer import generate_summary_stats, generate_auto_charts, generate_null_report
from agent import suggest_insights, answer_question
from utils import load_csv

# Global state
current_df = None
chat_history = []


def handle_question(user_message, history):
    global current_df, chat_history

    if current_df is None:
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": "Please upload a CSV file first."})
        return history, None

    if not user_message.strip():
        return history, None

    our_history = []
    for i in range(0, len(history) - 1, 2):
        if i + 1 < len(history):
            our_history.append((history[i]["content"], history[i+1]["content"]))

    result_text, chart = answer_question(current_df, user_message, our_history)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": result_text})
    chat_history.append((user_message, result_text))

    return history, chart


def on_upload(file):
    global current_df, chat_history

    if file is None:
        return ("Upload a CSV file first.",
                "Upload a CSV file first.",
                None,
                gr.Dropdown(choices=[], visible=False),
                [])

    df, error = load_csv(file)
    if error:
        return (f"**Error:** {error}", "", None,
                gr.Dropdown(choices=[], visible=False), [])

    current_df = df
    chat_history = []

    stats = generate_summary_stats(df)
    charts = generate_auto_charts(df)
    null_chart = generate_null_report(df)
    insights = suggest_insights(df)

    chart_names = [f"Chart {i+1}" for i in range(len(charts))]

    return (stats, insights, null_chart,
            gr.Dropdown(choices=chart_names, visible=True, value="Chart 1"),
            charts)


def show_chart(selection, all_charts):
    if not selection or not all_charts:
        return None
    idx = int(selection.split(" ")[1]) - 1
    if 0 <= idx < len(all_charts):
        return all_charts[idx]
    return None


with gr.Blocks() as demo:

    gr.Markdown("""
    # Data Analyst Agent
    **Powered by Llama 3 + Groq | Built by Abhishek Khandge**

    Upload any CSV to get instant stats, charts, AI insights, and chat with your data.
    """)

    with gr.Row():
        file_input = gr.File(
            label="Upload CSV File",
            file_types=[".csv"],
            scale=2
        )
        upload_btn = gr.Button("Analyze Dataset", variant="primary", scale=1)

    with gr.Tabs():

        with gr.Tab("Summary Stats"):
            stats_output = gr.Markdown(value="Upload a CSV to see stats.")

        with gr.Tab("Auto Charts"):
            chart_selector = gr.Dropdown(
                label="Select chart to view",
                choices=[],
                visible=False
            )
            charts_output = gr.Plot(label="Chart")

        with gr.Tab("Missing Values"):
            null_chart_output = gr.Plot(label="Missing Values Report")

        with gr.Tab("AI Insights"):
            insights_output = gr.Markdown(value="Upload a CSV to get AI insights.")

        with gr.Tab("Chat with Your Data"):
            chatbot = gr.Chatbot(
                label="Ask anything about your data",
                height=400
            )
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="e.g. What is the average salary? Which city has the most records?",
                    label="Your question",
                    scale=4
                )
                send_btn = gr.Button("Ask", variant="primary", scale=1)
            chat_chart_output = gr.Plot(label="Chart from your question")

            gr.Markdown("""
            **Example questions:**
            - What is the average value of [column]?
            - Which [category] appears the most?
            - Show me a bar chart of [column]
            - Are there any outliers in [column]?
            - How many rows have missing values?
            """)

    all_charts_state = gr.State([])

    upload_btn.click(
        fn=on_upload,
        inputs=[file_input],
        outputs=[stats_output, insights_output, null_chart_output,
                 chart_selector, all_charts_state]
    )

    chart_selector.change(
        fn=show_chart,
        inputs=[chart_selector, all_charts_state],
        outputs=[charts_output]
    )

    send_btn.click(
        fn=handle_question,
        inputs=[chat_input, chatbot],
        outputs=[chatbot, chat_chart_output]
    ).then(fn=lambda: "", outputs=[chat_input])

    chat_input.submit(
        fn=handle_question,
        inputs=[chat_input, chatbot],
        outputs=[chatbot, chat_chart_output]
    ).then(fn=lambda: "", outputs=[chat_input])


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=8000
    )


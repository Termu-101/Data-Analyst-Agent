
<div align="center">

# 🤖 Data Analyst Agent

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Llama_3-70B-FF6B35?style=for-the-badge&logo=meta&logoColor=white"/>
<img src="https://img.shields.io/badge/Groq-API-F55036?style=for-the-badge&logo=groq&logoColor=white"/>
<img src="https://img.shields.io/badge/Gradio-6.0-FF7C00?style=for-the-badge&logo=gradio&logoColor=white"/>
<img src="https://img.shields.io/badge/AWS-Elastic_Beanstalk-FF9900?style=for-the-badge&logo=amazonwebservices&logoColor=white"/>
<img src="https://img.shields.io/badge/Pandas-3.0-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
<img src="https://img.shields.io/badge/Plotly-6.0-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"/>

<br/>

> **Upload any CSV. Get instant charts, stats, and AI insights. Ask questions in plain English. Get real answers.**

<br/>

![Demo](http://data-agent-env.eba-ckzamic8.us-east-1.elasticbeanstalk.com/)

</div>

---

## 📌 What is this?

A fully deployed AI-powered data analysis tool that turns any CSV file into an interactive analytics dashboard — with a conversational interface powered by **Llama 3.3 70B**.

Unlike generic chatbots, this agent actually **executes code on your real data**. It doesn't hallucinate numbers — it writes pandas code, runs it, and returns verified results.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Auto Charts** | Histograms, bar charts, scatter plots, box plots, correlation heatmaps — generated instantly |
| 📋 **Summary Stats** | Mean, median, std dev, min/max, null counts, unique values per column |
| 💡 **AI Insights** | Llama 3 analyzes your schema and suggests the most interesting patterns to explore |
| 🔍 **Missing Value Report** | Visual breakdown of data quality issues across all columns |
| 💬 **Natural Language Q&A** | Ask questions like *"which city has the most sales?"* and get real pandas-powered answers |
| 🧠 **Conversation Memory** | Remembers previous questions in the session for follow-up queries |

---

## 🏗️ How It Works

```
User uploads CSV
       │
       ▼
 pandas reads file
 stats generated instantly
       │
       ▼
 Schema extracted ──────────────────────────────────────┐
 (column names, types, sample rows)                     │
       │                                                 ▼
       ▼                                        Llama 3 suggests
 Charts auto-generated                          5 insights + 3 questions
 from column types                              + data quality flags
       │
       │   User asks a question in chat
       ▼
 Schema + question → Llama 3
       │
       ▼
 Llama 3 writes pandas code
       │
       ▼
 Code executes on real dataframe
       │
       ▼
 Result returned as text or interactive chart
```


---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **LLM** | Llama 3.3 70B via Groq | Free, fast (~1s response), 70B parameters for high accuracy |
| **Data Engine** | pandas 3.0 | Industry standard for tabular data manipulation |
| **Charts** | Plotly 6.0 | Interactive, beautiful, works in browser |
| **UI** | Gradio 6.0 | Production-grade ML UI with minimal code |
| **Cloud** | AWS Elastic Beanstalk | Auto-scaling, managed deployment, free tier |
| **Code Gen** | LLM → exec() pipeline | LLM writes pandas code, Python runs it on real data |

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Free [Groq API key](https://console.groq.com) (no credit card needed)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Termu-101/data-analyst-agent
cd data-analyst-agent

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo "GROQ_API_KEY=your_key_here" > .env

# 5. Run
python app.py
```

Open `http://localhost:8000` in your browser.

---

## 📁 Project Structure

```
data-analyst-agent/
│
├── app.py              # Gradio UI — all tabs, buttons, event handlers
├── agent.py            # LLM brain — insight generation + Q&A + code execution
├── analyzer.py         # Data engine — stats + auto chart generation
├── utils.py            # Helpers — CSV loading, schema extraction, formatting
│
├── requirements.txt    # All dependencies pinned
├── Procfile            # Tells AWS how to start the app
│
├── .env                # Your API key (never committed)
├── .gitignore
└── .ebignore
```

---

## 💬 Example Questions You Can Ask

```
"What is the average salary by department?"
"Which product category has the highest revenue?"
"Show me a bar chart of sales by region"
"Are there any outliers in the age column?"
"How many rows have missing values?"
"What is the correlation between price and quantity?"
"Which month had the most orders?"
"Show me the top 5 customers by total spend"
```

---

## 🧠 What Makes This Different From Just Calling an API

Most "AI data tools" send your entire dataset to an LLM and ask it to summarize. This breaks with large files, leaks your data, and produces hallucinated statistics.

This agent uses a **code generation + execution** architecture:

```python
# What a naive tool does (wrong)
prompt = f"Here is my data: {entire_dataframe}. What is the average age?"
# ❌ Hits token limits, slow, hallucination-prone

# What this agent does (right)
prompt = f"Schema: {schema_only}. Write pandas code to find average age."
code = llm.generate(prompt)       # LLM writes: result = df['age'].mean()
result = exec(code, {"df": df})   # Python executes it on real data
# ✅ Fast, accurate, works on any size dataset
```

---

## ☁️ AWS Deployment

This app is deployed on **AWS Elastic Beanstalk** (free tier):

```bash
# Initialize
eb init

# Deploy
eb create data-agent-env --instance-type t2.micro

# Set API key securely on AWS
eb setenv GROQ_API_KEY=your_key_here

# Open live app
eb open

# Push updates
eb deploy
```


---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Elastic Beanstalk                 │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌───────────────────┐  │
│  │  app.py  │───▶│analyzer  │───▶│  pandas + plotly  │  │
│  │ (Gradio) │    │  .py     │    │  (local compute)  │  │
│  │          │    └──────────┘    └───────────────────┘  │
│  │          │    ┌──────────┐    ┌───────────────────┐  │
│  │          │───▶│ agent.py │───▶│  Groq API         │  │
│  │          │    │          │    │  Llama 3.3 70B    │  │
│  └──────────┘    └──────────┘    └───────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                    EC2 t2.micro
                    Python 3.11
                    512MB swap
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GROQ_API_KEY` | Your Groq API key from console.groq.com | ✅ Yes |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**Built by Abhishek Khandge**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/abhishek-khandge)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Termu-101)

*MS Data Science @ UMass Amherst | IEEE Published Researcher*

</div>

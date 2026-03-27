import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import format_value



# This creates a clean summary of the dataset and returns a markdown formatted string for display

def generate_summary_stats(df: pd.DataFrame) -> str:
    lines = []
    lines.append("## Dataset Overview")
    lines.append(f"- **Rows:** {df.shape[0]:,}")
    lines.append(f"- **Columns:** {df.shape[1]}")
    lines.append(f"- **Total cells:** {df.shape[0] * df.shape[1]:,}")
    lines.append(f"- **Missing values:** {df.isnull().sum().sum():,} "
                 f"({100 * df.isnull().sum().sum() / (df.shape[0] * df.shape[1]):.1f}%)")

    # Separate numeric and categorical columns
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    lines.append(f"\n**Numeric columns ({len(numeric_cols)}):** {', '.join(numeric_cols) if numeric_cols else 'None'}")
    lines.append(f"**Categorical columns ({len(categorical_cols)}):** {', '.join(categorical_cols) if categorical_cols else 'None'}")

    # Stats for numeric columns
    if numeric_cols:
        lines.append("\n## Numeric Column Statistics")
        for col in numeric_cols:
            s = df[col].dropna()
            lines.append(f"\n**{col}**")
            lines.append(f"  - Mean: {format_value(s.mean())}")
            lines.append(f"  - Median: {format_value(s.median())}")
            lines.append(f"  - Std Dev: {format_value(s.std())}")
            lines.append(f"  - Min: {format_value(s.min())} | Max: {format_value(s.max())}")
            lines.append(f"  - Nulls: {df[col].isnull().sum()}")

    # Stats for categorical columns
    if categorical_cols:
        lines.append("\n## Categorical Column Statistics")
        for col in categorical_cols:
            top_vals = df[col].value_counts().head(3)
            lines.append(f"\n**{col}**")
            lines.append(f"  - Unique values: {df[col].nunique()}")
            lines.append(f"  - Nulls: {df[col].isnull().sum()}")
            lines.append(f"  - Top 3 values: {', '.join([f'{v} ({c})' for v, c in top_vals.items()])}")

    return "\n".join(lines)



# Automatically generates charts for most relevant columns
 
def generate_auto_charts(df: pd.DataFrame) -> list:
    
    charts = []
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Chart 1: Distribution of each numeric column (histogram)
    for col in numeric_cols[:4]:  # max 4 to avoid overload
        fig = px.histogram(
            df, x=col,
            title=f"Distribution of {col}",
            color_discrete_sequence=["#4F86C6"],
            template="plotly_white"
        )
        fig.update_layout(bargap=0.1)
        charts.append(fig)

    # Chart 2: Bar chart for categorical columns (top 10 values)
    for col in categorical_cols[:3]:  # max 3
        counts = df[col].value_counts().head(10).reset_index()
        counts.columns = [col, 'count']
        fig = px.bar(
            counts, x=col, y='count',
            title=f"Top values in {col}",
            color_discrete_sequence=["#5BAD6F"],
            template="plotly_white"
        )
        charts.append(fig)

    # Chart 3: Correlation heatmap (if 2+ numeric columns)
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig = px.imshow(
            corr,
            title="Correlation Heatmap",
            color_continuous_scale="RdBu_r",
            aspect="auto",
            template="plotly_white"
        )
        charts.append(fig)

    # Chart 4: Scatter plot between first two numeric columns
    if len(numeric_cols) >= 2:
        fig = px.scatter(
            df, x=numeric_cols[0], y=numeric_cols[1],
            title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
            color_discrete_sequence=["#E07B54"],
            template="plotly_white",
            opacity=0.6
        )
        charts.append(fig)

    # Chart 5: Box plots for numeric columns (shows outliers)
    if numeric_cols:
        fig = px.box(
            df[numeric_cols[:5]],  # max 5 columns in one box plot
            title="Box Plots — Spread and Outliers",
            template="plotly_white"
        )
        charts.append(fig)

    return charts


# Creates a bar chart showing missing values %

def generate_null_report(df: pd.DataFrame) -> go.Figure:
    
    null_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    null_pct = null_pct[null_pct > 0]  # only show columns that have nulls

    if null_pct.empty:
        # Return a simple "no nulls" figure
        fig = go.Figure()
        fig.add_annotation(
            text="No missing values found in this dataset",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(title="Missing Values Report", template="plotly_white")
        return fig

    fig = px.bar(
        x=null_pct.index,
        y=null_pct.values,
        title="Missing Values by Column (%)",
        labels={"x": "Column", "y": "Missing %"},
        color=null_pct.values,
        color_continuous_scale="Reds",
        template="plotly_white"
    )
    return fig

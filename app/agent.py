import os

from dotenv import load_dotenv
from openai import OpenAI

from app.config import DB_PATH
from app.db import run_query
from app.prompt import (get_error_message, get_success_message,
                        get_system_prompt)

# Load environment variables
load_dotenv()

# Initialize OpenAI client - handle missing API key gracefully
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key or api_key == "your-openai-api-key-here":
    client = None
else:
    client = OpenAI(api_key=api_key)


def nl_to_sql(question: str) -> str:
    if not client:
        return "SELECT * FROM customers; -- AI ikke tilgængelig"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    sql = response.choices[0].message.content.strip()

    # Clean up SQL - remove markdown formatting if present
    if sql.startswith("```sql"):
        sql = sql.replace("```sql", "").replace("```", "").strip()
    elif sql.startswith("```"):
        sql = sql.replace("```", "").strip()

    return sql


def ask(question: str):
    if not client:
        return {"error": get_error_message("no_api_key")}

    sql = nl_to_sql(question)
    print(f"{get_success_message('query_generated')} {sql}")

    try:
        result = run_query(sql)

        # Hvis ingen data fundet, lav AI forklaring
        if not result:
            explanation = generate_explanation(question, sql)
            return {"sql": sql, "rows": result, "ai_explanation": explanation}

        return {"sql": sql, "rows": result}
    except Exception as e:
        return {"sql": sql, "error": str(e)}


def generate_explanation(question: str, sql: str) -> str:
    """
    Genererer en kort AI forklaring når der ikke findes data
    """
    if not client:
        return "Ingen data fundet for denne forespørgsel."

    explanation_prompt = f"""
Du er en hjælpsom CRM assistent. En bruger spurgte: "{question}"

SQL query var: {sql}

Der blev ikke fundet nogen data. Giv et kort, venskabeligt svar (max 2 sætninger) på dansk der:
1. Bekræfter hvad de spurgte om
2. Foreslår hvad de kunne prøve i stedet

Vær positiv og hjælpsom.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": explanation_prompt}],
            temperature=0.7,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except:
        return "Der blev ikke fundet nogen data for denne forespørgsel. Prøv at udvide søgekriterierne eller vælg et af eksemplerne ovenfor."

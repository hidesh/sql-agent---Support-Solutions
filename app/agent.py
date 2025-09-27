import os
from openai import OpenAI
from app.db import run_query
from app.config import DB_PATH
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client - handle missing API key gracefully
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key or api_key == "your-openai-api-key-here":
    client = None
else:
    client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
Du er en CRM-assistent for Support Solutions - et IT-konsulentfirma. 
Du modtager spørgsmål i naturligt sprog og skal returnere gyldige SQL queries til SQLite CRM-databasen.

DATABASER OG TABELLER:

customers (kunder):
- id, company_name, contact_person, email, phone, address, city, postal_code
- industry, company_size, status, customer_since, total_value, notes

consultants (konsulenter):
- id, name, email, phone, speciality, hourly_rate, status, hire_date

deals (muligheder/salg):
- id, customer_id, title, description, value, probability
- stage (Prospecting, Qualified, Proposal, Negotiation, Closed Won, Closed Lost)
- expected_close_date, assigned_consultant_id

projects (projekter):
- id, customer_id, deal_id, name, description, project_type
- status (Planning, In Progress, On Hold, Completed, Cancelled)
- start_date, end_date, budget, actual_cost, hours_estimated, hours_actual

project_consultants (projekt-konsulent kobling):
- project_id, consultant_id, role, hours_allocated, hours_worked

activities (aktiviteter):
- id, customer_id, deal_id, project_id, consultant_id
- type (Call, Meeting, Email, Task, Note), subject, description
- activity_date, duration, outcome

EKSEMPLER:
- "Vis alle kunder" → SELECT * FROM customers;
- "Hvilke deals har vi?" → SELECT * FROM deals;
- "Aktive projekter" → SELECT * FROM projects WHERE status = 'In Progress';
- "Top konsulenter" → SELECT * FROM consultants ORDER BY hourly_rate DESC;
- "Deals der lukker i år" → SELECT * FROM deals WHERE expected_close_date BETWEEN '2024-01-01' AND '2024-12-31';

VIGTIGE REGLER:
- Brug altid JOIN når du skal kombinere data fra flere tabeller
- Brug danske termer i WHERE clauses (f.eks. 'In Progress' for aktive projekter)
- Inkluder altid relevante kolonner - ikke kun *
- Sorter resultater logisk (efter dato, værdi, navn)

Skriv KUN SQL'en, intet andet.
"""

def nl_to_sql(question: str) -> str:
    if not client:
        return "SELECT * FROM customers; -- AI ikke tilgængelig"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        temperature=0
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
        return {"error": "OpenAI API key mangler"}
    
    sql = nl_to_sql(question)
    print(f"📝 Genereret SQL: {sql}")

    try:
        result = run_query(sql)
        return {"sql": sql, "rows": result}
    except Exception as e:
        return {"sql": sql, "error": str(e)}
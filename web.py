import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from app.agent import ask, generate_explanation
from app.db import run_query

app = Flask(__name__)
app.secret_key = "support-solutions-crm-secret-key"


@app.route("/", methods=["GET", "POST"])
def index():
    # Check if AI is available
    ai_available = (
        os.environ.get("OPENAI_API_KEY")
        and os.environ.get("OPENAI_API_KEY") != "your-openai-api-key-here"
    )

    if request.method == "POST":
        question = request.form.get("question")

        if not ai_available:
            session["error"] = (
                "⚠️ AI-funktionalitet er ikke tilgængelig. Tilføj din OpenAI API key til .env filen for fuld CRM funktionalitet."
            )
            session["sql"] = "-- AI ikke tilgængelig - prøv med eksemplerne"
        else:
            try:
                result = ask(question)
                session["sql"] = result.get("sql", "")
                session["question"] = question

                if "error" in result:
                    session["error"] = result["error"]
                else:
                    answer = result.get("rows", [])
                    session["answer"] = answer
                    session.pop("error", None)

                    # Generate AI explanation if no results found
                    if not answer or len(answer) == 0:
                        try:
                            explanation = generate_explanation(question, session["sql"])
                            session["ai_explanation"] = explanation
                        except Exception as e:
                            # Fallback explanation if AI fails
                            session["ai_explanation"] = (
                                f"🤖 Jeg kunne ikke finde data for dit spørgsmål '{question}'. Prøv at omformulere eller brug en af eksemplerne til inspiration."
                            )

            except Exception as e:
                session["error"] = f"Der opstod en fejl: {str(e)}"
                session["sql"] = "-- Fejl ved generering af CRM query"

        # Redirect to prevent resubmission
        return redirect(url_for("index"))

    # GET request - get data from session
    question = session.pop("question", None)
    answer = session.pop("answer", None)
    sql = session.pop("sql", None)
    error = session.pop("error", None)
    ai_explanation = session.pop("ai_explanation", None)

    return render_template(
        "index.html",
        question=question,
        sql=sql,
        answer=answer,
        error=error,
        ai_explanation=ai_explanation,
        ai_available=ai_available,
    )


@app.route("/api/crm/stats")
def crm_stats():
    """API endpoint to get CRM statistics"""
    try:
        # Get key CRM metrics
        stats = {}

        # Customer stats
        customer_stats = run_query(
            "SELECT COUNT(*) as total, COUNT(CASE WHEN status = 'Active' THEN 1 END) as active FROM customers"
        )
        stats["customers"] = (
            customer_stats[0] if customer_stats else {"total": 0, "active": 0}
        )

        # Deal stats
        deal_stats = run_query(
            "SELECT COUNT(*) as total, SUM(value) as total_value, AVG(probability) as avg_probability FROM deals WHERE stage NOT IN ('Closed Won', 'Closed Lost')"
        )
        stats["deals"] = (
            deal_stats[0]
            if deal_stats
            else {"total": 0, "total_value": 0, "avg_probability": 0}
        )

        # Project stats
        project_stats = run_query(
            "SELECT COUNT(*) as total, COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as active FROM projects"
        )
        stats["projects"] = (
            project_stats[0] if project_stats else {"total": 0, "active": 0}
        )

        # Consultant stats
        consultant_stats = run_query(
            "SELECT COUNT(*) as total, AVG(hourly_rate) as avg_rate FROM consultants WHERE status = 'Active'"
        )
        stats["consultants"] = (
            consultant_stats[0] if consultant_stats else {"total": 0, "avg_rate": 0}
        )

        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/crm/dashboard")
def dashboard_data():
    """API endpoint for dashboard widgets"""
    try:
        # Recent activities
        recent_activities = run_query(
            """
            SELECT a.type, a.subject, a.activity_date, c.company_name 
            FROM activities a 
            LEFT JOIN customers c ON a.customer_id = c.id 
            ORDER BY a.activity_date DESC 
            LIMIT 5
        """
        )

        # Top deals by value
        top_deals = run_query(
            """
            SELECT d.title, d.value, d.stage, c.company_name
            FROM deals d
            LEFT JOIN customers c ON d.customer_id = c.id
            WHERE d.stage NOT IN ('Closed Won', 'Closed Lost')
            ORDER BY d.value DESC
            LIMIT 5
        """
        )

        # Project status distribution
        project_status = run_query(
            """
            SELECT status, COUNT(*) as count
            FROM projects
            GROUP BY status
        """
        )

        return jsonify(
            {
                "success": True,
                "data": {
                    "recent_activities": recent_activities,
                    "top_deals": top_deals,
                    "project_status": project_status,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/customers")
def customers():
    """Dedicated customers page"""
    try:
        # Get all customers with stats
        customers_data = run_query(
            """
            SELECT c.*, 
                   COUNT(d.id) as deal_count,
                   COALESCE(SUM(d.value), 0) as total_deal_value,
                   COUNT(p.id) as project_count
            FROM customers c
            LEFT JOIN deals d ON c.id = d.customer_id
            LEFT JOIN projects p ON c.id = p.customer_id
            GROUP BY c.id
            ORDER BY c.company_name
        """
        )

        # Customer statistics
        stats = {
            "total": len(customers_data),
            "active": len([c for c in customers_data if c["status"] == "Active"]),
            "total_value": sum([c["total_deal_value"] for c in customers_data]),
            "avg_projects": (
                sum([c["project_count"] for c in customers_data]) / len(customers_data)
                if customers_data
                else 0
            ),
        }

        return render_template("customers.html", customers=customers_data, stats=stats)

    except Exception as e:
        return render_template("customers.html", customers=[], stats={}, error=str(e))


@app.route("/deals")
def deals():
    """Dedicated deals page"""
    try:
        # Get all deals with customer and consultant info
        deals_data = run_query(
            """
            SELECT d.*, c.company_name as customer_name,
                   co.name as consultant_name
            FROM deals d
            LEFT JOIN customers c ON d.customer_id = c.id
            LEFT JOIN consultants co ON d.assigned_consultant_id = co.id
            ORDER BY d.value DESC
        """
        )

        # Deal statistics
        stats = {
            "total": len(deals_data),
            "total_value": sum([d["value"] for d in deals_data]),
            "won": len([d for d in deals_data if d["stage"] == "Closed Won"]),
            "pipeline_value": sum(
                [
                    d["value"]
                    for d in deals_data
                    if d["stage"] not in ["Closed Won", "Closed Lost"]
                ]
            ),
        }

        return render_template("deals.html", deals=deals_data, stats=stats)

    except Exception as e:
        return render_template("deals.html", deals=[], stats={}, error=str(e))


@app.route("/projects")
def projects():
    """Dedicated projects page"""
    try:
        # Get all projects with customer info and consultant assignments
        projects_data = run_query(
            """
            SELECT p.*, c.company_name as customer_name,
                   GROUP_CONCAT(co.name, ', ') as consultant_names,
                   COUNT(pc.consultant_id) as consultant_count
            FROM projects p
            LEFT JOIN customers c ON p.customer_id = c.id
            LEFT JOIN project_consultants pc ON p.id = pc.project_id
            LEFT JOIN consultants co ON pc.consultant_id = co.id
            GROUP BY p.id
            ORDER BY p.start_date DESC
        """
        )

        # Project statistics
        stats = {
            "total": len(projects_data),
            "active": len([p for p in projects_data if p["status"] == "In Progress"]),
            "total_budget": sum([p["budget"] for p in projects_data]),
            "avg_budget": (
                sum([p["budget"] for p in projects_data]) / len(projects_data)
                if projects_data
                else 0
            ),
        }

        return render_template("projects.html", projects=projects_data, stats=stats)

    except Exception as e:
        return render_template("projects.html", projects=[], stats={}, error=str(e))


@app.route("/consultants")
def consultants():
    """Dedicated consultants page"""
    try:
        # Get all consultants with project assignments
        consultants_data = run_query(
            """
            SELECT c.*, 
                   COUNT(pc.project_id) as project_count,
                   GROUP_CONCAT(p.name, ', ') as current_projects
            FROM consultants c
            LEFT JOIN project_consultants pc ON c.id = pc.consultant_id
            LEFT JOIN projects p ON pc.project_id = p.id AND p.status = 'In Progress'
            GROUP BY c.id
            ORDER BY c.name
        """
        )

        # Consultant statistics
        stats = {
            "total_consultants": len(consultants_data),
            "active_consultants": len(
                [c for c in consultants_data if c["status"] == "Active"]
            ),
            "avg_rate": (
                sum([c["hourly_rate"] for c in consultants_data])
                / len(consultants_data)
                if consultants_data
                else 0
            ),
            "total_projects": sum([c["project_count"] for c in consultants_data]),
        }

        return render_template(
            "consultants.html", consultants=consultants_data, stats=stats
        )

    except Exception as e:
        return render_template(
            "consultants.html", consultants=[], stats={}, error=str(e)
        )


@app.route("/activities")
def activities():
    """Dedicated activities page"""
    try:
        # Get all activities with related customer and consultant info
        activities_data = run_query(
            """
            SELECT a.*, 
                   c.company_name as customer_name,
                   co.name as consultant_name
            FROM activities a
            LEFT JOIN customers c ON a.customer_id = c.id
            LEFT JOIN consultants co ON a.consultant_id = co.id
            ORDER BY a.activity_date DESC
        """
        )

        # Activity statistics
        from datetime import datetime, timedelta

        today = datetime.now()
        week_ago = today - timedelta(days=7)

        stats = {
            "total_activities": len(activities_data),
            "this_week": len(
                [
                    a
                    for a in activities_data
                    if a["activity_date"]
                    and a["activity_date"] >= week_ago.strftime("%Y-%m-%d")
                ]
            ),
            "meetings_calls": len(
                [a for a in activities_data if a["type"] in ["Meeting", "Call"]]
            ),
            "follow_ups": len(
                [a for a in activities_data if a["outcome"] == "Follow-up needed"]
            ),
        }

        return render_template(
            "activities.html",
            activities=activities_data,
            stats=stats,
            current_date=today.strftime("%Y-%m-%d"),
        )

    except Exception as e:
        return render_template("activities.html", activities=[], stats={}, error=str(e))


@app.route("/api/status")
def status():
    """API endpoint to check system status"""
    ai_available = (
        os.environ.get("OPENAI_API_KEY")
        and os.environ.get("OPENAI_API_KEY") != "your-openai-api-key-here"
    )

    # Test database connection with CRM data
    db_available = True
    try:
        test_result = run_query("SELECT COUNT(*) as count FROM customers LIMIT 1")
        customer_count = test_result[0]["count"] if test_result else 0
    except Exception as e:
        db_available = False
        customer_count = 0

    return jsonify(
        {
            "ai_available": ai_available,
            "db_available": db_available,
            "customer_count": customer_count,
            "status": "healthy" if ai_available and db_available else "partial",
            "system": "Support Solutions CRM",
        }
    )


if __name__ == "__main__":
    print("🚀 Starter Support Solutions CRM System...")
    print(f"🌐 Åbn din browser på: http://localhost:5001")

    ai_available = (
        os.environ.get("OPENAI_API_KEY")
        and os.environ.get("OPENAI_API_KEY") != "your-openai-api-key-here"
    )
    if not ai_available:
        print("⚠️  OpenAI API key ikke fundet - AI funktioner er deaktiveret")
        print("💡 Tilføj din API key til .env filen for fuld CRM funktionalitet")
    else:
        print("✅ AI-drevne CRM funktioner er aktiveret")

    print("📊 CRM features: Kunder, Deals, Projekter, Konsulenter, Aktiviteter")
    app.run(debug=True, host="0.0.0.0", port=5001)

from app.agent import ask
from app.db import run_action, run_query


def main():
    print("Tester databaseforbindelsen...\n")

    # 1. Læs de første 5 kunder
    customers = run_query("SELECT * FROM customers LIMIT 5;")
    print("De første kunder:", customers)

    # 2. Slet eksisterende test kunde hvis den findes
    run_action("DELETE FROM customers WHERE id = ?", (999,))

    # 3. Indsæt en ny kunde (demo)
    run_action(
        "INSERT INTO customers (id, company_name, contact_person, email, city) "
        "VALUES (?, ?, ?, ?, ?)",
        (999, "Test Kunde ApS", "Test Manager", "test@example.com", "Copenhagen"),
    )
    print("Ny kunde indsat.")

    # 4. Hent den nye kunde
    new_customer = run_query("SELECT * FROM customers WHERE id = ?", (999,))
    print("Ny kunde hentet:", new_customer)

    # 5. Vis alle kunder fra Copenhagen
    copenhagen_customers = run_query(
        "SELECT * FROM customers WHERE city = ?", ("Copenhagen",)
    )
    print("Kunder fra Copenhagen:", copenhagen_customers)

    # 6. Test AI agent
    print("\n=== AI Agent Test ===")
    print("Spørgsmål: Hent alle kunder fra Denmark")
    result = ask("Hent alle kunder fra Denmark")
    print("AI Svar:", result)


if __name__ == "__main__":
    main()

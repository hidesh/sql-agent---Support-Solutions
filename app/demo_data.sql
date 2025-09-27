-- Support Solutions CRM Database Schema
-- Komplet CRM system til IT-konsulentvirksomhed

-- Slet eksisterende tabeller
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS deals;
DROP TABLE IF EXISTS consultants;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS project_consultants;

-- Kunder tabel
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    industry TEXT,
    company_size TEXT, -- Small, Medium, Large, Enterprise
    status TEXT DEFAULT 'Active', -- Active, Inactive, Prospect
    customer_since DATE,
    total_value REAL DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Konsulenter tabel
CREATE TABLE consultants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    speciality TEXT, -- DevOps, Cloud, Security, Web Development, etc.
    hourly_rate REAL,
    status TEXT DEFAULT 'Active', -- Active, Inactive, On Leave
    hire_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Deals/Muligheder tabel
CREATE TABLE deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    value REAL NOT NULL,
    probability INTEGER DEFAULT 50, -- 0-100%
    stage TEXT DEFAULT 'Prospecting', -- Prospecting, Qualified, Proposal, Negotiation, Closed Won, Closed Lost
    expected_close_date DATE,
    assigned_consultant_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(assigned_consultant_id) REFERENCES consultants(id)
);

-- Projekter tabel
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    deal_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT, -- Website, App Development, Cloud Migration, IT Support, Security Audit
    status TEXT DEFAULT 'Planning', -- Planning, In Progress, On Hold, Completed, Cancelled
    start_date DATE,
    end_date DATE,
    budget REAL,
    actual_cost REAL DEFAULT 0,
    hours_estimated REAL,
    hours_actual REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(deal_id) REFERENCES deals(id)
);

-- Projekt-konsulent koblingstabel (mange-til-mange)
CREATE TABLE project_consultants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    consultant_id INTEGER,
    role TEXT, -- Lead, Developer, Designer, Project Manager
    hours_allocated REAL,
    hours_worked REAL DEFAULT 0,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(consultant_id) REFERENCES consultants(id)
);

-- Aktiviteter tabel (calls, meetings, emails, etc.)
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    deal_id INTEGER,
    project_id INTEGER,
    consultant_id INTEGER,
    type TEXT NOT NULL, -- Call, Meeting, Email, Task, Note
    subject TEXT NOT NULL,
    description TEXT,
    activity_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER, -- i minutter
    outcome TEXT, -- Positive, Neutral, Negative, Follow-up needed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(deal_id) REFERENCES deals(id),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(consultant_id) REFERENCES consultants(id)
);

-- Indsæt Support Solutions konsulenter
INSERT INTO consultants (name, email, phone, speciality, hourly_rate, hire_date) VALUES
('Lars Nielsen', 'lars@support-solutions.dk', '+45 20 12 34 56', 'Cloud Architecture', 1200, '2022-01-15'),
('Emma Sørensen', 'emma@support-solutions.dk', '+45 30 23 45 67', 'Web Development', 950, '2022-06-20'),
('Marcus Johansen', 'marcus@support-solutions.dk', '+45 40 34 56 78', 'DevOps & Security', 1100, '2021-09-10'),
('Sofia Andersen', 'sofia@support-solutions.dk', '+45 50 45 67 89', 'Project Management', 800, '2023-03-01'),
('Oliver Hansen', 'oliver@support-solutions.dk', '+45 60 56 78 90', 'Database & Backend', 1000, '2022-11-12');

-- Indsæt kunder (danske virksomheder)
INSERT INTO customers (company_name, contact_person, email, phone, address, city, postal_code, industry, company_size, customer_since, total_value) VALUES
('TechStart ApS', 'Peter Madsen', 'peter@techstart.dk', '+45 70 12 34 56', 'Innovationsvej 12', 'København', '2100', 'Software', 'Small', '2023-02-15', 250000),
('Nordisk Handel A/S', 'Anne Larsen', 'anne@nordiskhandel.dk', '+45 80 23 45 67', 'Handelsgade 45', 'Aarhus', '8000', 'Retail', 'Medium', '2022-08-20', 580000),
('GreenEnergy Solutions', 'Michael Kristensen', 'mk@greenenergy.dk', '+45 90 34 56 78', 'Bæredygtighedsvej 8', 'Odense', '5000', 'Energy', 'Large', '2021-12-05', 1200000),
('FinanceHub Danmark', 'Camilla Thomsen', 'camilla@financehub.dk', '+45 31 45 67 89', 'Bankgade 23', 'København', '1000', 'Finance', 'Enterprise', '2022-01-30', 2100000),
('MedTech Innovations', 'Jens Poulsen', 'jens@medtech.dk', '+45 21 56 78 90', 'Sundhedsvej 15', 'Aalborg', '9000', 'Healthcare', 'Medium', '2023-05-12', 450000),
('Danish Logistics Pro', 'Mette Hansen', 'mette@logisticspro.dk', '+45 32 67 89 01', 'Transportvej 67', 'Esbjerg', '6700', 'Logistics', 'Large', '2022-11-08', 890000),
('EduTech Solutions', 'Thomas Møller', 'thomas@edutech.dk', '+45 42 78 90 12', 'Læringsgade 34', 'København', '2200', 'Education', 'Small', '2024-01-20', 125000),
('SmartHome Danmark', 'Line Pedersen', 'line@smarthome.dk', '+45 52 89 01 23', 'Teknologivej 19', 'Herning', '7400', 'Technology', 'Small', '2023-09-15', 180000);

-- Indsæt deals (potentielle og aktuelle projekter)
INSERT INTO deals (customer_id, title, description, value, probability, stage, expected_close_date, assigned_consultant_id) VALUES
(1, 'Cloud Migration Projekt', 'Migrering af eksisterende infrastruktur til Azure cloud', 350000, 80, 'Proposal', '2024-12-15', 1),
(2, 'E-commerce Platform Upgrade', 'Modernisering af webshop med ny funktionalitet', 280000, 60, 'Qualified', '2025-01-30', 2),
(3, 'Sikkerhedsaudit og Implementering', 'Komplet sikkerhedsgennemgang og forbedringer', 450000, 90, 'Negotiation', '2024-11-20', 3),
(4, 'BI Dashboard System', 'Business Intelligence løsning med real-time data', 680000, 70, 'Proposal', '2025-02-28', 5),
(5, 'Telemedicin Platform', 'Udvikling af digital sundhedsplatform', 520000, 45, 'Prospecting', '2025-03-15', 2),
(6, 'Logistics Tracking System', 'Real-time sporing og optimering af leverancer', 390000, 85, 'Negotiation', '2024-12-10', 1),
(7, 'Online Learning Platform', 'E-learning platform til uddannelsesinstitutioner', 220000, 40, 'Qualified', '2025-04-01', 2),
(8, 'Smart Home Integration', 'IoT løsning til hjemmeautomatisering', 150000, 30, 'Prospecting', '2025-05-20', 3);

-- Indsæt aktuelle projekter
INSERT INTO projects (customer_id, deal_id, name, description, project_type, status, start_date, end_date, budget, hours_estimated) VALUES
(3, 3, 'GreenEnergy Security Overhaul', 'Implementering af nye sikkerhedsforanstaltninger', 'Security Audit', 'In Progress', '2024-09-01', '2024-12-15', 450000, 300),
(4, 4, 'FinanceHub BI Implementation', 'Business Intelligence dashboard udvikling', 'App Development', 'Planning', '2024-11-01', '2025-02-28', 680000, 450),
(1, 1, 'TechStart Cloud Setup', 'Azure cloud migration og setup', 'Cloud Migration', 'In Progress', '2024-08-15', '2024-12-15', 350000, 250),
(2, 2, 'Nordisk Handel Webshop', 'E-commerce platform modernisering', 'Website', 'Planning', '2024-12-01', '2025-03-30', 280000, 200);

-- Tilknyt konsulenter til projekter
INSERT INTO project_consultants (project_id, consultant_id, role, hours_allocated) VALUES
(1, 3, 'Lead', 120),
(1, 5, 'Developer', 100),
(1, 4, 'Project Manager', 80),
(2, 5, 'Lead', 200),
(2, 2, 'Developer', 150),
(2, 4, 'Project Manager', 100),
(3, 1, 'Lead', 150),
(3, 3, 'Developer', 80),
(3, 4, 'Project Manager', 20),
(4, 2, 'Lead', 120),
(4, 5, 'Developer', 60),
(4, 4, 'Project Manager', 20);

-- Indsæt aktiviteter (meetings, calls, osv.)
INSERT INTO activities (customer_id, deal_id, project_id, consultant_id, type, subject, description, activity_date, duration, outcome) VALUES
(1, 1, 3, 1, 'Meeting', 'Kick-off møde', 'Projektopstart og krav-gennemgang', '2024-08-15 10:00:00', 120, 'Positive'),
(3, 3, 1, 3, 'Call', 'Sikkerhedsgennemgang', 'Diskussion af sikkerhedsrisici og løsninger', '2024-09-20 14:30:00', 60, 'Follow-up needed'),
(4, 4, 2, 5, 'Meeting', 'Requirements Workshop', 'Detaljeret gennemgang af BI-krav', '2024-10-15 09:00:00', 180, 'Positive'),
(2, 2, NULL, 2, 'Email', 'Projektforslag sendt', 'Detaljeret projektforslag til webshop upgrade', '2024-10-20 16:00:00', 30, 'Neutral'),
(6, 6, NULL, 1, 'Meeting', 'Løsningsarkitektur', 'Præsentation af logistics tracking løsning', '2024-10-25 11:00:00', 90, 'Positive'),
(5, 5, NULL, 2, 'Call', 'Telemedicin krav', 'Indledende diskussion af platform-krav', '2024-10-28 13:00:00', 45, 'Neutral'),
(1, 1, 3, 4, 'Task', 'Projektplan opdatering', 'Revision af tidsplan baseret på feedback', '2024-10-30 15:00:00', 60, 'Positive');

-- Opdater faktiske værdier for igangværende projekter
UPDATE projects SET actual_cost = 180000, hours_actual = 120 WHERE id = 1; -- GreenEnergy Security
UPDATE projects SET actual_cost = 95000, hours_actual = 80 WHERE id = 3; -- TechStart Cloud
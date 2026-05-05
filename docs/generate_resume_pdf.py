from fpdf import FPDF, XPos, YPos

class Resume(FPDF):
    def header(self):
        pass

pdf = Resume(format='Letter')
pdf.add_page()
pdf.set_margins(15, 14, 15)
pdf.set_auto_page_break(auto=True, margin=14)

def section_header(pdf, text):
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(0, 5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(0, 0, 0)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 180, pdf.get_y())
    pdf.ln(1.5)

def body(pdf, text, bold=False, size=8.5):
    style = "B" if bold else ""
    pdf.set_font("Helvetica", style, size)
    pdf.multi_cell(0, 4.5, text)

def bullet(pdf, text, size=8.5):
    pdf.set_font("Helvetica", "", size)
    pdf.set_x(20)
    pdf.multi_cell(175, 4.5, f"*  {text}")

def two_col(pdf, left, right, left_bold=False, right_italic=False, size=8.5):
    lstyle = "B" if left_bold else ""
    rstyle = "I" if right_italic else ""
    pdf.set_font("Helvetica", lstyle, size)
    pdf.cell(133, 4.5, left)
    pdf.set_font("Helvetica", rstyle, size)
    pdf.cell(47, 4.5, right, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

# Name
pdf.set_font("Helvetica", "B", 15)
pdf.cell(0, 7, "Eliza Okome", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
pdf.set_font("Helvetica", "", 8.5)
pdf.cell(0, 4.5, "Los Angeles, CA  |  elizaokomee@gmail.com  |  (747) 230-7462  |  linkedin.com/in/eliza-okome", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
pdf.ln(2.5)

# Objective
section_header(pdf, "OBJECTIVE")
body(pdf, "Data analytics student seeking an entry-level analyst role where I can apply SQL, Python, and dashboard skills to monitor campaign performance, ensure data accuracy, and deliver actionable insights to cross-functional teams.")
pdf.ln(2)

# Education
section_header(pdf, "EDUCATION")
two_col(pdf, "Loyola Marymount University - BS, Information Systems & Business Analytics", "Expected May 2027", left_bold=True, right_italic=True)
body(pdf, "Transfer from Cal Poly Pomona  |  Dean's List - Spring 2025")
pdf.ln(1)
two_col(pdf, "California Polytechnic University, Pomona - BS, Computer Information Systems", "Dec 2024", left_bold=True, right_italic=True)
body(pdf, "Magna Cum Laude  |  Cum Laude")
pdf.ln(2)

# Skills
section_header(pdf, "SKILLS")
pdf.set_font("Helvetica", "B", 8.5)
pdf.write(4.5, "Technical: ")
pdf.set_font("Helvetica", "", 8.5)
pdf.write(4.5, "SQL (MySQL), Python, dbt, Snowflake, GitHub Actions, Streamlit, Excel (pivot tables, VLOOKUP), Data Entry")
pdf.ln(4.5)
pdf.set_font("Helvetica", "B", 8.5)
pdf.write(4.5, "Analytics: ")
pdf.set_font("Helvetica", "", 8.5)
pdf.write(4.5, "Star schema / dimensional modeling, KPI dashboards, campaign performance analysis, data quality testing, data integrity validation")
pdf.ln(4.5)
pdf.ln(2)

# Projects
section_header(pdf, "PROJECTS")
two_col(pdf, "Digital Marketing Analytics Pipeline  |  Analytics Engineering, LMU", "Spring 2026", left_bold=True, right_italic=True)
pdf.set_font("Helvetica", "I", 8.5)
pdf.cell(0, 4.5, "github.com/elizaokome/marketing-analytics-pipeline", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(1)
bullet(pdf, "Built an end-to-end ELT pipeline using Python, Snowflake, and dbt to extract financial services complaint data from a REST API, modeling it into a star schema (fact + dimension tables) tracking complaint KPIs by product, geography, and company to identify high-dissatisfaction markets for campaign targeting.")
bullet(pdf, "Designed dbt staging and mart models with automated data quality tests; deployed an interactive Streamlit dashboard connected live to Snowflake for real-time campaign performance monitoring.")
bullet(pdf, "Automated the pipeline via GitHub Actions on a schedule; managed credentials via environment variables; built a knowledge base synthesizing 15+ industry sources into actionable insights on financial product complaint trends and lead gen targeting opportunities.")
bullet(pdf, "Identified credit card complaints as the highest-growth category (+67% in 2024) and Texas as a top high-volume state; produced ad hoc targeting recommendations to prioritize credit monitoring and refinance campaigns in high-complaint geographies and presented findings to course stakeholders.")
pdf.ln(2)

# Experience
section_header(pdf, "EXPERIENCE")

two_col(pdf, "Office of the Registrar Student Assistant - Loyola Marymount University", "Aug 2025 - Present", left_bold=True, right_italic=True)
body(pdf, "Westchester, CA")
bullet(pdf, "Manage front office operations as first point of contact for students, staff, and visitors; handle high-volume inquiries via phone and email with precision and professionalism.")
bullet(pdf, "Provide administrative support including data entry, filing, and cross-team collaboration in a fast-paced environment.")
pdf.ln(2)

two_col(pdf, "Stockroom Student Assistant - Cal Poly Pomona", "Feb 2024 - May 2024", left_bold=True, right_italic=True)
body(pdf, "Pomona, CA")
bullet(pdf, "Supported lab technicians with weekly preparation, data entry, and equipment tracking; managed window service during lab instruction.")
pdf.ln(2)

two_col(pdf, "Team Leader - Cal Poly Pomona Academic Project", "Sep 2023 - Nov 2023", left_bold=True, right_italic=True)
body(pdf, "Pomona, CA")
bullet(pdf, "Led a team researching food insecurity solutions; coordinated deadlines, synthesized findings, and maintained equitable task distribution.")
pdf.ln(2)

two_col(pdf, "Black Student Union Treasurer - Chaminade College Preparatory", "Oct 2021 - May 2023", left_bold=True, right_italic=True)
body(pdf, "West Hills, CA")
bullet(pdf, "Managed club finances, organized fundraising events, and maintained accurate financial records throughout the year.")

pdf.output("/Users/elizaokome/isba-4715/data-analyst-fintech/docs/resume_eliza_okome.pdf")
print("PDF generated successfully.")

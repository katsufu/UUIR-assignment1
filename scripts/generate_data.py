import json
import random
import re
from datetime import datetime, timedelta

def generate_random_date(start_year=2020):
    start_date = datetime(year=start_year, month=1, day=1)
    end_date = datetime.now()
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_data(num_records=10000):
    positions = [
        {
            "title": "Software Engineer",
            "desc": "Design and develop scalable web applications and microservices.",
            "req": "Bachelor's in CS, 3+ years experience with Python/Java, strong problem-solving skills.",
            "keywords": ["Python", "Java", "Docker", "Microservices", "SQL", "Git"]
        },
        {
            "title": "Data Scientist",
            "desc": "Analyze large datasets to extract actionable insights and build predictive models.",
            "req": "Master's in Statistics or CS, 2+ years experience with ML frameworks, strong SQL.",
            "keywords": ["Python", "Machine Learning", "SQL", "TensorFlow", "Pandas", "Statistics"]
        },
        {
            "title": "HR Manager",
            "desc": "Oversee recruitment, employee relations, and performance management.",
            "req": "Bachelor's in HR or related field, 5+ years experience in HR management.",
            "keywords": ["Recruitment", "Employee Relations", "Performance Management", "Communication"]
        },
        {
            "title": "Accountant",
            "desc": "Manage financial records, auditing, and tax compliance.",
            "req": "CPA or equivalent, 3+ years in corporate accounting.",
            "keywords": ["Excel", "Auditing", "Tax Compliance", "Financial Reporting"]
        },
        {
            "title": "Product Manager",
            "desc": "Lead cross-functional teams to deliver high-quality software products.",
            "req": "4+ years experience in product management, agile methodologies, strong leadership.",
            "keywords": ["Agile", "Scrum", "Roadmapping", "Leadership", "Jira"]
        },
        {
            "title": "DevOps Engineer",
            "desc": "Implement and maintain CI/CD pipelines, monitor system performance, and ensure reliability.",
            "req": "3+ years experience in DevOps, proficiency with AWS/Azure, Kubernetes.",
            "keywords": ["AWS", "Kubernetes", "CI/CD", "Jenkins", "Terraform", "Linux"]
        },
        {
            "title": "UX/UI Designer",
            "desc": "Create intuitive user interfaces and engaging user experiences for web and mobile.",
            "req": "Portfolio demonstrating strong design skills, 2+ years experience, Figma/Sketch proficiency.",
            "keywords": ["Figma", "Sketch", "Wireframing", "Prototyping", "User Research"]
        },
        {
            "title": "Frontend Developer",
            "desc": "Build responsive and interactive web interfaces using modern JavaScript frameworks.",
            "req": "Bachelor's in CS, 2+ years experience with React or Vue.js, strong CSS skills.",
            "keywords": ["JavaScript", "React", "Vue.js", "CSS", "HTML", "TypeScript"]
        },
        {
            "title": "Backend Developer",
            "desc": "Develop robust server-side logic, APIs, and database architecture.",
            "req": "3+ years experience with Node.js or Go, experience with RESTful APIs.",
            "keywords": ["Node.js", "Go", "API Design", "PostgreSQL", "Redis", "Backend"]
        },
        {
            "title": "QA Engineer",
            "desc": "Design and execute automated and manual tests to ensure software quality.",
            "req": "2+ years experience in software testing, proficiency in Selenium or Cypress.",
            "keywords": ["Selenium", "Cypress", "Testing", "Automation", "Bug Tracking"]
        },
        {
            "title": "Security Analyst",
            "desc": "Monitor networks for security breaches, investigate violations, and implement security measures.",
            "req": "Bachelor's in Cybersecurity, 3+ years experience, CISSP or CEH certification.",
            "keywords": ["Cybersecurity", "Network Security", "Penetration Testing", "Risk Assessment"]
        },
        {
            "title": "Marketing Specialist",
            "desc": "Develop and execute digital marketing campaigns to drive brand awareness and lead generation.",
            "req": "Bachelor's in Marketing, 2+ years experience with SEO/SEM and content strategy.",
            "keywords": ["SEO", "SEM", "Content Marketing", "Google Analytics", "Social Media"]
        },
        {
            "title": "Business Analyst",
            "desc": "Bridge the gap between IT and business using data analytics to assess processes and determine requirements.",
            "req": "3+ years experience as a BA, strong analytical skills, experience with SQL and Tableau.",
            "keywords": ["Business Analysis", "Requirements Gathering", "Tableau", "SQL", "Process Modeling"]
        },
        {
            "title": "Machine Learning Engineer",
            "desc": "Design and implement machine learning applications and infrastructure.",
            "req": "Master's in CS or AI, 3+ years experience deploying ML models to production.",
            "keywords": ["Python", "PyTorch", "MLOps", "Model Deployment", "Deep Learning"]
        },
        {
            "title": "Technical Support Specialist",
            "desc": "Provide tier 2 technical support for software products and resolve customer issues.",
            "req": "2+ years in IT support, excellent communication skills, troubleshooting expertise.",
            "keywords": ["Customer Support", "Troubleshooting", "Ticketing Systems", "Communication"]
        }
    ]

    reasons_accepted = [
        "Applicant meets all requirements and shows strong domain knowledge.",
        "Excellent technical skills and fits well with the team culture.",
        "Strong relevant experience and performed exceptionally in the interview.",
        "Unique background with highly applicable skills that exceeded expectations.",
        "Demonstrated exceptional problem-solving abilities during the technical assessment.",
        "Possesses a rare combination of technical expertise and leadership qualities.",
        "Impressive portfolio and previous project experience perfectly align with our needs.",
        "Showed great enthusiasm and a deep understanding of our company's mission.",
        "Highly recommended by previous employers and passed all screening stages with flying colors.",
        "Outstanding communication skills combined with solid technical foundations.",
        "Brings valuable industry-specific knowledge that will benefit the team immediately.",
        "Proved to be highly adaptable and capable of learning new technologies quickly.",
        "Showcased innovative thinking during the case study presentation.",
        "Perfect match for the current seniority level required by the department.",
        "Demonstrated a strong commitment to continuous learning and professional development."
    ]

    reasons_rejected = [
        "Lacks the minimum required experience years.",
        "Missing key technical skills required for the position.",
        "Did not perform well during the technical assessment.",
        "Communication skills did not meet the role's requirements.",
        "Experience does not align with the specific needs of the department.",
        "Salary expectations exceeded the budget allocated for this role.",
        "Found a candidate whose experience more closely matched our current tech stack.",
        "Did not demonstrate the necessary problem-solving framework during the case study.",
        "Cultural fit assessment indicated potential conflicts with the team's working style.",
        "Unable to provide satisfactory references from previous employers.",
        "Candidate lacked the required certifications for this specific level.",
        "Project portfolio did not show the depth of experience required for a senior role.",
        "Withdrew application during the interview process.",
        "Answers during the behavioral interview raised concerns about adaptability.",
        "Did not pass the required background check or verification process.",
        "Lack of clarity in explaining past projects and contributions.",
        "Insufficient experience with the specific tools used by our team.",
        "Availability timeline did not align with our urgent hiring needs.",
        "Demonstrated a lack of passion for the industry during the final interview."
    ]

    data = []
    
    for i in range(num_records):
        pos = random.choice(positions)
        
        # Determine experience years (sometimes underqualified, sometimes overqualified)
        match = re.search(r'(\d+)\+', pos["req"])
        base_exp = int(match.group(1)) if match else 3
        exp_years = random.randint(max(0, base_exp - 2), base_exp + 7)
        
        # Determine keywords applicant actually has
        applicant_keywords = random.sample(pos["keywords"], k=random.randint(1, len(pos["keywords"])))
        # Add some random other skills sometimes
        if random.random() > 0.4:
            extra_skills = ["C++", "React", "Public Speaking", "Project Management", "Marketing", "SAP", "Excel", "Data Analysis", "Leadership", "Spanish", "Ruby"]
            applicant_keywords.extend(random.sample(extra_skills, k=random.randint(1, 3)))
            
        # Build a synthetic CV text
        cv_variations = [
            f"Highly motivated professional seeking the {pos['title']} position. I bring {exp_years} years of hands-on experience in the field. My core competencies include: {', '.join(applicant_keywords)}. ",
            f"Dedicated {pos['title']} with {exp_years} years of experience. Skilled in {', '.join(applicant_keywords)}. Looking to leverage my background to contribute effectively to your team. ",
            f"Experienced candidate applying for {pos['title']}. Over {exp_years} years working in dynamic environments. Proficient in {', '.join(applicant_keywords)}. ",
            f"Results-driven individual targeting a {pos['title']} role. I have {exp_years} years of relevant industry experience and strong expertise in {', '.join(applicant_keywords)}. "
        ]
        cv_text = random.choice(cv_variations)
        
        if exp_years >= base_exp:
            cv_text += random.choice([
                "I have successfully led projects and delivered results that align with your requirements.",
                "My past achievements demonstrate my ability to exceed expectations.",
                "I am confident that my extensive experience makes me an ideal fit for this role."
            ])
        else:
            cv_text += random.choice([
                "I am a fast learner and eager to grow my skills to meet the challenges of this role.",
                "While I am building my experience, my passion and dedication will drive my success.",
                "I am looking for an opportunity to develop my expertise further in a supportive environment."
            ])
            
        # Determine outcome
        # Basic heuristic + randomness
        meets_exp = exp_years >= base_exp
        has_keywords = len(set(applicant_keywords).intersection(set(pos["keywords"]))) / len(pos["keywords"]) > 0.6
        
        score = (meets_exp * 0.5) + (has_keywords * 0.5) + random.uniform(-0.3, 0.3)
        
        if score > 0.65:
            result = "Accepted"
            reason = random.choice(reasons_accepted)
        else:
            result = "Rejected"
            if not meets_exp and random.random() > 0.3:
                reason = "Lacks the minimum required experience years."
            elif not has_keywords and random.random() > 0.3:
                reason = "Missing key technical skills required for the position."
            else:
                reason = random.choice(reasons_rejected)
                
        recruitment_date = generate_random_date().strftime("%Y-%m-%d")

        data.append({
            "recruitment_date": recruitment_date,
            "opening_position": pos["title"],
            "description": pos["desc"],
            "requirement": pos["req"],
            "keywords_for_recruitment": pos["keywords"],
            "cv": cv_text,
            "experience_years": exp_years,
            "keywords_from_applicants": applicant_keywords,
            "result": result,
            "reason_for_result": reason
        })

        if i % 1000 == 0 and i > 0:
            print(f"Generated {i} records...")

    # Sort by date
    data.sort(key=lambda x: x["recruitment_date"])
    
    with open("data/recruitment_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully generated {num_records} recruitment records in data/recruitment_data.json")

if __name__ == "__main__":
    generate_data(10000)

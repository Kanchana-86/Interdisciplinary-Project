import streamlit as st
import pandas as pd
from Backend import load_data, load_course_list, get_recommendations_from_dataframe

# --- Page Configuration ---
st.set_page_config(
    page_title="Internship Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 1. STUDENT PAGES ---

def show_student_dashboard():
    """
    Student dashboard to view live profile and internship matches.
    """
    st.header("🎓 Student Dashboard")
    st.markdown("Select your completed courses below to see your skills and matches update in real-time.")

    # Load the list of available courses from Backend
    all_courses = load_course_list()
    # Load the full data for processing from Backend
    df, all_skills = load_data()
    
    if not all_courses:
        st.stop()  # Stop the app if the course list couldn't be loaded

    # --- User Input ---
    with st.container(border=True):
        st.subheader("1. Select Your Completed Courses")
        selected_courses = st.multiselect(
            "Courses",
            options=all_courses,
            label_visibility="collapsed"
        )

    # --- Get Data from Backend ---
    if selected_courses:
        st.session_state.api_data = get_recommendations_from_dataframe(selected_courses, df, all_skills)
    else:
        # If no courses are selected, reset the data
        st.session_state.api_data = {"recommendations": [], "student_skills": [], "skill_gap": []}

    # --- Dashboard "K-Cards" ---
    st.subheader("2. Your Live Profile")
    
    # Get data from session state
    api_data = st.session_state.api_data
    recommendations = api_data.get('recommendations', [])
    student_skills = api_data.get('student_skills', [])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.container(border=True).metric(
            label="Courses Completed",
            value=len(selected_courses)
        )
    with col2:
        st.container(border=True).metric(
            label="Skills Identified",
            value=len(student_skills)
        )
    with col3:
        st.container(border=True).metric(
            label="Internships Matched",
            value=len(recommendations)
        )
    
    st.divider()

    # --- Display Results ---
    st.subheader("3. Your Skill Profile")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.success("✅ Your Acquired Skills")
            if student_skills:
                skills_md = ", ".join(f"`{s}`" for s in student_skills)
                st.markdown(skills_md)
            else:
                st.info("No skills found. Select one or more courses above.")
    
    with col2:
        with st.container(border=True):
            # --- Interactive Skill Gap ---
            st.warning("🔍 Specific Skill Gap")
            
            if not recommendations:
                st.info("Select courses to match with internships, then check your gap here.")
            else:
                # Create dropdown of matched internships
                internship_options = {f"{rec['company']} - {rec['matched_course']}": rec for rec in recommendations}
                selected_internship_title = st.selectbox(
                    "Select an internship to see your skill gap:",
                    options=internship_options.keys()
                )
                
                if selected_internship_title:
                    selected_internship = internship_options[selected_internship_title]
                    required_skills = set(selected_internship.get('required_skills', []))
                    my_skills = set(student_skills)
                    
                    specific_gap = required_skills - my_skills
                    has_skills = required_skills.intersection(my_skills)
                    
                    st.markdown("**Skills You Have:**")
                    if has_skills:
                        st.markdown(", ".join(f"`{s}`" for s in has_skills), help="You meet these requirements!")
                    else:
                        st.markdown("None for this role.")
                        
                    st.markdown("**Skills You Need:**")
                    if specific_gap:
                        st.markdown(", ".join(f"`{s}`" for s in specific_gap), help="Work on these to be a perfect match!")
                    else:
                        st.markdown("None. You're a perfect match!")

    st.divider()
    
    # --- Internship Matches ---
    st.subheader("4. Your Internship Matches")

    if not recommendations:
        st.info("No internship matches found. Try selecting different courses.")
    else:
        st.success(f"Found {len(recommendations)} matching internship(s)!")
        for rec in recommendations:
            with st.expander(f"**{rec['company']}** (Matched on: *{rec['matched_course']}*)"):
                st.markdown(f"**Description:** {rec['description']}")
                st.markdown(f"**Location:** {rec['location']} | **Stipend:** {rec['stipend']}")
                skills_list = rec.get('required_skills', [])
                skills_md = ", ".join(f"`{s}`" for s in skills_list)
                st.markdown(f"**Required Skills:** {skills_md}")
                st.markdown("**Apply Here (LinkedIn):**")
                urls = rec.get('linkedin_urls', [])
                for url in urls:
                    st.markdown(f"- [{url}]({url})")

def show_psychometric_test():
    """
    A mocked-up page for the psychometric test.
    """
    st.header("🧠 Psychometric Test & Career Fit")
    st.markdown("For each statement, select the option that feels **most** like you, even if it's not a perfect fit.")
    
    with st.container(border=True):
        st.subheader("Personality Inventory")
        
        # We store the results in variables
        q1 = st.radio("1. I feel more energized when I...", ("Spend time with a group", "Have quiet time alone"), horizontal=True, key="q1")
        q2 = st.radio("2. When learning something new, I prefer to...", ("Understand the underlying theory", "Jump in and try it myself"), horizontal=True, key="q2")
        q3 = st.radio("3. I am more of a...", ("Realistic person", "Imaginative person"), horizontal=True, key="q3")
        q4 = st.radio("4. When making a decision, I prioritize...", ("Logic and facts", "People's feelings and values"), horizontal=True, key="q4")
        q5 = st.radio("5. I prefer my work to be...", ("Organized and planned", "Spontaneous and flexible"), horizontal=True, key="q5")
        q6 = st.radio("6. I would rather...", ("Finish one task before starting another", "Work on multiple things at once"), horizontal=True, key="q6")
        q7 = st.radio("7. In discussions, I am more likely to...", ("Observe and listen", "Share my ideas"), horizontal=True, key="q7")
        q8 = st.radio("8. I am more interested in...", ("What is actual", "What is possible"), horizontal=True, key="q8")
        q9 = st.radio("9. I find it more appealing to be...", ("Fair and just", "Merciful and compassionate"), horizontal=True, key="q9")
        q10 = st.radio("10. My workspace is usually...", ("Tidy and organized", "A bit cluttered but functional"), horizontal=True, key="q10")
        q11 = st.radio("11. I'd rather be known as...", ("A practical thinker", "A creative thinker"), horizontal=True, key="q11")
        q12 = st.radio("12. When I have a free weekend, I...", ("Plan activities in advance", "See what happens"), horizontal=True, key="q12")
        q13 = st.radio("13. I trust...", ("My experiences", "My intuition"), horizontal=True, key="q13")
        q14 = st.radio("14. I find it easier to...", ("Analyze a situation objectively", "Put myself in other's shoes"), horizontal=True, key="q14")
        q15 = st.radio("15. I am more comfortable with...", ("Following a clear set of rules", "Having freedom and few rules"), horizontal=True, key="q15")

        st.divider()
        
        if st.button("Submit Test", use_container_width=True, type="primary"):
            st.success("Test Submitted!")
            st.subheader("Your Career Profile")
            
            # --- Real Scoring Logic ---
            scores = {
                "Analytical": 0,
                "Creative": 0,
                "Organizer": 0,
                "People-Oriented": 0
            }

            # --- Tally the scores based on all 15 answers ---
            if q1 == "Spend time with a group": scores["People-Oriented"] += 1
            elif q1 == "Have quiet time alone": scores["Analytical"] += 1 

            if q2 == "Understand the underlying theory": scores["Analytical"] += 1
            
            if q3 == "Realistic person": scores["Organizer"] += 1
            elif q3 == "Imaginative person": scores["Creative"] += 1

            if q4 == "Logic and facts": scores["Analytical"] += 1
            elif q4 == "People's feelings and values": scores["People-Oriented"] += 1

            if q5 == "Organized and planned": scores["Organizer"] += 1
            elif q5 == "Spontaneous and flexible": scores["Creative"] += 1

            if q6 == "Finish one task before starting another": scores["Organizer"] += 1
            elif q6 == "Work on multiple things at once": scores["Creative"] += 1

            if q7 == "Observe and listen": scores["Analytical"] += 1
            elif q7 == "Share my ideas": scores["People-Oriented"] += 1

            if q8 == "What is actual": scores["Organizer"] += 1
            elif q8 == "What is possible": scores["Creative"] += 1
            
            if q9 == "Fair and just": scores["Analytical"] += 1
            elif q9 == "Merciful and compassionate": scores["People-Oriented"] += 1

            if q10 == "Tidy and organized": scores["Organizer"] += 1
            elif q10 == "A bit cluttered but functional": scores["Creative"] += 1

            if q11 == "A practical thinker": scores["Analytical"] += 1
            elif q11 == "A creative thinker": scores["Creative"] += 1
            
            if q12 == "Plan activities in advance": scores["Organizer"] += 1
            elif q12 == "See what happens": scores["Creative"] += 1

            if q13 == "My experiences": scores["Analytical"] += 1
            elif q13 == "My intuition": scores["Creative"] += 1

            if q14 == "Analyze a situation objectively": scores["Analytical"] += 1
            elif q14 == "Put myself in other's shoes": scores["People-Oriented"] += 1

            if q15 == "Following a clear set of rules": scores["Organizer"] += 1
            elif q15 == "Having freedom and few rules": scores["Creative"] += 1

            # --- Find the highest scoring profile ---
            sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            primary_profile = sorted_scores[0][0]
            top_score = sorted_scores[0][1]
            second_score = sorted_scores[1][1]

            if top_score == second_score:
                primary_profile = "Balanced"

            # --- Display the result ---
            if primary_profile == "Analytical":
                st.info("You seem to be an **Analytical Thinker**! You prioritize logic and practical solutions. We'll recommend roles in analysis, finance, and R&D.")
            elif primary_profile == "Creative":
                st.info("You seem to be a **Creative Type**! You enjoy exploring new possibilities. We'll recommend roles in design, marketing, and strategy.")
            elif primary_profile == "Organizer":
                st.info("You seem to be an **Organizer**! You thrive in structured environments. We'll recommend roles in project management, operations, and administration.")
            elif primary_profile == "People-Oriented":
                st.info("You seem to be a **People-Oriented**! You connect well with others. We'll recommend roles in human resources, customer success, and team leadership.")
            else: 
                st.info("You have a **Balanced Profile**! You show a mix of traits from different types. We'll recommend a variety of roles that match your skills.")

            st.write("Your Score Breakdown:")
            st.dataframe(pd.DataFrame.from_dict(scores, orient='index', columns=['Score']), use_container_width=True)

def show_resume_builder():
    """
    A mocked-up page for the resume builder.
    """
    st.header("📄 Resume Builder")
    st.markdown("Enter your details to generate a role-specific resume.")
    
    # --- Resume Type Selector ---
    resume_type = st.radio("1. Select Resume Type", ("Technical", "Managerial", "Creative"), horizontal=True)
    
    with st.form("resume_form"):
        st.subheader("2. Personal Details")
        col1, col2 = st.columns(2)
        col1.text_input("Full Name", key="full_name")
        col2.text_input("Email", key="email")
        st.text_input("Phone Number", key="phone")
        st.text_area("Professional Summary", key="summary")
        
        # --- Detailed Education ---
        st.subheader("3. Education")
        col1, col2 = st.columns(2)
        col1.text_input("Degree (e.g., B.Tech Computer Science)", key="degree")
        col2.text_input("College/University", key="college")
        col1.text_input("Year of Completion (e.g., 2025)", key="grad_year")
        col2.text_input("Marks/CGPA (e.g., 8.5)", key="cgpa")
        
        # --- Multiple Projects with Tags ---
        st.subheader("4. Projects")
        st.markdown("Project 1")
        col1, col2 = st.columns([2, 1])
        col1.text_input("Project 1 Title", key="p1_title")
        col2.multiselect("Project 1 Tags", ["Technical", "Social", "Art", "Management"], key="p1_tags")
        st.text_area("Project 1 Description", placeholder="Describe your project...", key="p1_desc")

        st.markdown("Project 2")
        col1, col2 = st.columns([2, 1])
        col1.text_input("Project 2 Title", key="p2_title")
        col2.multiselect("Project 2 Tags", ["Technical", "Social", "Art", "Management"], key="p2_tags")
        st.text_area("Project 2 Description", placeholder="Describe another project...", key="p2_desc")
        
        st.subheader("5. Experience")
        st.text_area("Internship/Work Experience", placeholder="Describe your experience...", key="experience")
        
        submitted = st.form_submit_button("Generate Resume", use_container_width=True, type="primary")
        
        if submitted:
            st.success(f"Successfully generated your '{resume_type}' resume!")
            
            # Determine the tag to highlight based on resume_type
            target_tag = ""
            if resume_type == "Technical":
                target_tag = "Technical"
            elif resume_type == "Managerial":
                target_tag = "Management"
            elif resume_type == "Creative":
                target_tag = "Art"

            st.info(f"Based on your selection, we are highlighting projects with the **'{target_tag}'** tag.")

            # Build the resume content string
            resume_content = f"""
# {st.session_state.full_name}'s {resume_type} Resume

## Personal Details
- **Email:** {st.session_state.email}
- **Phone:** {st.session_state.phone}

## Professional Summary
{st.session_state.summary}

## Education
- **Degree:** {st.session_state.degree}
- **College:** {st.session_state.college}
- **Year:** {st.session_state.grad_year}
- **CGPA:** {st.session_state.cgpa}

## Experience
{st.session_state.experience}

## Projects (Highlighting: '{target_tag}')

### {st.session_state.p1_title} {"(✨ HIGHLIGHTED)" if target_tag in st.session_state.p1_tags else ""}
- **Tags:** {', '.join(st.session_state.p1_tags)}
- **Description:** {st.session_state.p1_desc}

### {st.session_state.p2_title} {"(✨ HIGHLIGHTED)" if target_tag in st.session_state.p2_tags else ""}
- **Tags:** {', '.join(st.session_state.p2_tags)}
- **Description:** {st.session_state.p2_desc}
"""
            
            st.session_state.generated_resume_data = resume_content
            st.session_state.generated_resume_filename = f"{st.session_state.full_name}_{resume_type}_Resume.txt"
            st.session_state.resume_generated = True
            
    # Download button OUTSIDE the form
    if st.session_state.get("resume_generated", False):
        st.download_button(
            label="Download Resume as .txt File",
            data=st.session_state.generated_resume_data, 
            file_name=st.session_state.generated_resume_filename,
            mime="text/plain", 
            use_container_width=True
        )
        st.session_state.resume_generated = False

def show_personal_settings():
    """
    A mocked-up page for editing personal profile information.
    """
    st.header("👤 Personal Settings")
    st.markdown("Update your personal information, photo, and resume.")

    with st.container(border=True):
        st.subheader("Profile Information")
        
        c1, c2 = st.columns(2)
        c1.text_input("Full Name", value="Your Name")
        c2.text_input("Date of Birth", value="01/01/2002")
        
        c1, c2 = st.columns(2)
        c1.text_input("Email", value="your.email@example.com")
        c2.text_input("Contact Number", value="+91 98765 43210")

        st.text_input("LinkedIn ID (username)", value="your-linkedin-id")
        
        st.subheader("Update Photo & Resume")
        c1, c2 = st.columns(2)
        c1.file_uploader("Upload Profile Photograph", type=["png", "jpg", "jpeg"])
        c2.file_uploader("Upload Master Resume (PDF)", type=["pdf"])

        st.subheader("Change Password")
        st.text_input("Current Password", type="password")
        st.text_input("New Password", type="password")
        st.text_input("Confirm New Password", type="password")

        if st.button("Save Changes", use_container_width=True, type="primary"):
            st.success("Your information has been updated! (Mock)")

# --- 2. RECRUITER PAGES ---

def show_manage_applications():
    """
    Page to manage applicants for a specific job.
    """
    job_title = st.session_state.view_job
    st.header(f"📮 Manage Applicants: {job_title}")
    
    if st.button("← Back to Dashboard"):
        st.session_state.view_job = None
        st.rerun()
    
    # Get the list of applicants for this job from session state
    applicants = st.session_state.mock_applicants.get(job_title, [])
    
    if not applicants:
        st.info("No applicants for this position yet.")
        return

    st.subheader("Pending Applications")
    
    for applicant in applicants:
        expander_label = f"**{applicant['name']}** |  Status: {applicant['status']}"
        
        with st.expander(expander_label):
            col1, col2 = st.columns([2, 1.2])

            with col1:
                st.subheader("Mock Profile View")
                st.markdown(f"**Email:** {applicant['name'].lower().replace(' ','_')}@email.com")
                st.markdown(f"**Skills:** {applicant['skills']}")
                st.bar_chart({"Profile Match": 75})
                st.info("This is a mock profile view.")

            with col2:
                st.subheader("Actions")
                status = applicant['status']
                
                if status == "Pending":
                    if st.button("Shortlist", key=f"short_{applicant['id']}", use_container_width=True, type="primary"):
                        applicant['status'] = "Shortlisted"
                        st.rerun()
                    if st.button("Reject", key=f"rej_{applicant['id']}", use_container_width=True):
                        applicant['status'] = "Rejected"
                        st.rerun()
                
                elif status == "Shortlisted":
                    st.success("✅ Added to shortlist")
                    if st.button("Undo Shortlist", key=f"undo_{applicant['id']}", use_container_width=True):
                        applicant['status'] = "Pending"
                        st.rerun()
                
                elif status == "Rejected":
                    st.error("❌ Rejected for now")
                    if st.button("Undo Reject", key=f"undo_{applicant['id']}", use_container_width=True):
                        applicant['status'] = "Pending"
                        st.rerun()

def show_recruiter_dashboard():
    """
    Recruiter dashboard with live stats and job posting management.
    """
    # Page routing logic
    if 'view_job' in st.session_state and st.session_state.view_job:
        show_manage_applications()
        return
        
    st.header("📈 Recruiter Dashboard")
    st.markdown("Manage your internship postings and view matched candidates.")
    
    # --- Recruiter K-Cards ---
    st.subheader("Live Stats (Mock)")
    col1, col2, col3 = st.columns(3)
    col1.container(border=True).metric("Posted Internships", "3")
    col2.container(border=True).metric("Total Applicants", "96")
    col3.container(border=True).metric("Top Matches", "24")

    st.divider()
    
    with st.container(border=True):
        st.subheader("Your Posted Internships")
        
        mock_jobs = {
            "Web Developer Intern": "(32 Applicants, 8 Matches)",
            "Data Analyst Intern": "(19 Applicants, 4 Matches)",
            "UI/UX Designer": "(45 Applicants, 12 Matches)"
        }
        
        for job_title, stats in mock_jobs.items():
            if st.button(f"**{job_title}** {stats}", use_container_width=True, help=f"Click to manage applicants for {job_title}"):
                st.session_state.view_job = job_title
                st.rerun()

def show_post_internship_form():
    """
    Form for recruiters to post new internships.
    """
    st.header("📮 Post a New Internship")
    
    with st.form("internship_form"):
        st.text_input("Internship Title (e.g., 'Web Developer Intern')")
        st.text_input("Company Name")
        st.text_input("Location (e.g., 'Chennai' or 'Remote')")
        st.text_input("Stipend (e.g., '₹15,000/month')")
        st.text_area("Job Description")
        st.text_input("Required Skills (comma-separated, e.g., 'Python, React, SQL')")
        
        submitted = st.form_submit_button("Post Internship", use_container_width=True, type="primary")
        
        if submitted:
            st.success("Your internship has been posted!")

def show_candidate_search():
    """
    Page for searching candidates.
    """
    st.header("🔍 Candidate Search")
    st.markdown("Filter our student pool to find the perfect fit.")
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.multiselect("Filter by Skills", ["Python", "React", "SQL", "Figma", "Agile"])
        col2.multiselect("Filter by Course", ["Web Development", "Machine Learning", "Database Management"])
        col3.multiselect("Filter by Psychometric Fit", ["Analytical", "Creative", "Organizer"])
        
        if st.button("Search Candidates", use_container_width=True, type="primary"):
            st.subheader("Search Results (Mock Data)")
            st.info("Showing 3 candidates matching your criteria.")
            st.markdown("- **Priya Sharma** (Skills: `Python`, `SQL` | Fit: `Analytical`)")
            st.markdown("- **Rohan Verma** (Skills: `React`, `Figma` | Fit: `Creative`)")
            st.markdown("- **Anjali Singh** (Skills: `Python`, `Agile` | Fit: `Organizer`)")

# --- 3. LANDING/LOGIN PAGE ---

def show_landing_page():
    """
    The main landing page with simulated login/register forms.
    """
    st.title("Welcome to the Internship Recommendation Platform")
    st.markdown("Bridging the gap between learning and your future career.")
    
    with st.container(border=True):
        # Central "I am a:" toggle
        user_type = st.radio(
            "Are you a:",
            ("Student", "Recruiter"),
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Tabs for "Login" and "Register"
        login_tab, register_tab = st.tabs(["Login", "Register"])
        
        with login_tab:
            st.subheader("Login")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if login_user and login_pass:
                    # SIMULATE LOGIN
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type
                    st.session_state.username = login_user
                    st.rerun()
                else:
                    st.error("Please enter username and password.")

        with register_tab:
            st.subheader("Register")
            reg_user = st.text_input("Username", key="reg_user")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
            
            if st.button("Register", use_container_width=True):
                if not reg_user or not reg_pass:
                    st.error("Please enter username and password.")
                elif reg_pass != reg_pass_confirm:
                    st.error("Passwords do not match.")
                else:
                    # SIMULATE REGISTRATION
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type
                    st.session_state.username = reg_user
                    st.rerun()

# --- MAIN APPLICATION LOGIC ---

def main():
    """
    The main function that controls the app's flow.
    """
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'api_data' not in st.session_state:
        st.session_state.api_data = {
            "recommendations": [],
            "student_skills": [],
            "skill_gap": []
        }
    if 'view_job' not in st.session_state:
        st.session_state.view_job = None
    if 'mock_applicants' not in st.session_state:
        st.session_state.mock_applicants = {
            "Web Developer Intern": [
                {"id": 1, "name": "Priya Sharma", "skills": "Python, SQL", "status": "Pending"},
                {"id": 2, "name": "Rohan Verma", "skills": "React, Figma", "status": "Pending"},
                {"id": 3, "name": "Anjali Singh", "skills": "Python, Agile", "status": "Pending"},
            ],
            "Data Analyst Intern": [
                {"id": 4, "name": "Vikram Reddy", "skills": "Excel, SQL", "status": "Pending"},
                {"id": 5, "name": "Sonia Gupta", "skills": "Tableau, Python", "status": "Pending"},
            ],
            "UI/UX Designer": [
                {"id": 6, "name": "Aarav Khan", "skills": "Figma, User Research", "status": "Pending"},
            ]
        }
        for job in st.session_state.mock_applicants:
            for app in st.session_state.mock_applicants[job]:
                app['status'] = "Pending"

    # Check if the user is logged in
    if st.session_state.logged_in:
        # --- LOGGED-IN VIEW ---
        st.sidebar.header(f"Welcome, {st.session_state.username}!")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_type}")
        
        if st.session_state.user_type == "Student":
            student_pages = {
                "My Dashboard": show_student_dashboard,
                "Psychometric Test": show_psychometric_test,
                "Resume Builder": show_resume_builder,
                "Personal Settings": show_personal_settings,
            }
            page_choice = st.sidebar.radio("Navigation", options=student_pages.keys())
            student_pages[page_choice]()
            
        elif st.session_state.user_type == "Recruiter":
            recruiter_pages = {
                "My Dashboard": show_recruiter_dashboard,
                "Post New Internship": show_post_internship_form,
                "Search Candidates": show_candidate_search,
            }
            page_choice = st.sidebar.radio("Navigation", options=recruiter_pages.keys())
            recruiter_pages[page_choice]()
        
        st.sidebar.caption("Tip: You can collapse this panel by clicking the 'X' at the top.")
        
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.username = ""
            st.session_state.view_job = None
            st.session_state.api_data = {"recommendations": [], "student_skills": [], "skill_gap": []}
            st.rerun()

    else:
        # --- LOGGED-OUT VIEW ---
        show_landing_page()

if __name__ == "__main__":
    main()

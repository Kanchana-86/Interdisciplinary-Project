import streamlit as st
import pandas as pd
# import requests # No longer needed!

# --- Page Configuration ---
st.set_page_config(
    page_title="Internship Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- Backend Configuration ---
# We no longer need a backend URL
# BACKEND_URL = "http://127.0.0.1:5000/get_recommendations" 

# --- Data Loading for UI ---
EXCEL_PATH = "/home/BTECH_7TH_SEM/Desktop/Interdisiplinary Project/LinkedIn_Internships_Dataset.xlsx"

@st.cache_data  # Cache the data so it only loads once
def load_data():
    """
    Loads the full DataFrame and pre-processes it.
    This replaces the logic from Backend.py.
    """
    try:
        df = pd.read_excel(EXCEL_PATH)
        # Pre-process the data for easier lookup
        df['Course Title Lower'] = df['Course Title'].str.lower()
        
        # Create a set of all unique skills mentioned in the dataset
        all_skills = set()
        for skills_list in df['Skills'].dropna():
            skills = [s.strip() for s in skills_list.split(',')]
            all_skills.update(skills)
            
        print("✅ Data loaded and pre-processed successfully.")
        return df, all_skills
        
    except FileNotFoundError:
        st.error(f"Error: Could not find the dataset at {EXCEL_PATH}")
        return None, set()
    except Exception as e:
        st.error(f"Error loading course list: {e}")
        return None, set()

@st.cache_data
def load_course_list():
    """Loads only the unique list of course titles for the multiselect."""
    df, _ = load_data()
    if df is not None:
        courses = df['Course Title'].dropna().unique()
        return sorted(courses)
    return []

# --- NEW: This function replaces the Flask API ---
def get_recommendations_from_dataframe(selected_courses, df, all_skills):
    """
    This function replicates the logic from your Flask backend.
    """
    if df is None:
        return {"recommendations": [], "student_skills": [], "skill_gap": []}

    student_courses = [course.lower() for course in selected_courses]
    
    recommendations = []
    student_skills = set()

    # Find all matching rows in the DataFrame
    matches = df[df['Course Title Lower'].isin(student_courses)]

    if matches.empty:
        return {
            "message": "No matching courses found in our database.",
            "recommendations": [],
            "student_skills": [],
            "skill_gap": list(all_skills)
        }

    # Process the matches
    for _, row in matches.iterrows():
        # Add to student's skills
        current_skills = [s.strip() for s in row['Skills'].split(',')]
        student_skills.update(current_skills)
        
        # Split the LinkedIn URLs
        urls = [url.strip() for url in row['LinkedIn URLs'].split(',')]
        
        # Format the recommendation
        recommendations.append({
            "matched_course": row['Course Title'],
            "company": row['Company'],
            "location": row['Location'],
            "stipend": row['Stipend'],
            "description": row['Description'],
            "required_skills": current_skills,
            "linkedin_urls": urls
        })

    # Calculate skill gap
    skill_gap = list(all_skills - student_skills)

    # --- Format Response ---
    return {
        "recommendations": recommendations,
        "student_skills": sorted(list(student_skills)),
        "skill_gap": sorted(skill_gap)
    }

# --- 1. STUDENT PAGES ---

def show_student_dashboard():
    """
    This function is updated to call the new local function
    instead of the requests.post() API.
    """
    st.header("🎓 Student Dashboard")
    st.markdown("Select your completed courses below to see your skills and matches update in real-time.")

    # Load the list of available courses
    all_courses = load_course_list()
    # Load the full data for processing
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

    # --- MODIFIED: Live API Call is now a local function call ---
    if selected_courses:
        # This one line REPLACES the entire 'try...except requests' block
        st.session_state.api_data = get_recommendations_from_dataframe(selected_courses, df, all_skills)
    
    else:
        # If no courses are selected, reset the data
        st.session_state.api_data = {"recommendations": [], "student_skills": [], "skill_gap": []}

    # --- NEW: Dashboard "K-Cards" (Request #3) ---
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
            # --- NEW: Interactive Skill Gap (Request #6) ---
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
    st.markdown("Answer these questions to help us understand your work preferences.")
    
    with st.container(border=True):
        st.subheader("Personality Inventory")
        q1 = st.radio("I prefer to work:", ("In a team", "Individually"))
        q2 = st.radio("I enjoy:", ("Solving complex problems", "Creative and artistic tasks", "Organizing and planning"))
        q3 = st.radio("I am more:", ("Detail-oriented", "A 'big picture' thinker"))
        
        if st.button("Submit Test", use_container_width=True):
            st.success("Test Submitted!")
            st.subheader("Your Career Profile (Example)")
            if q2 == "Solving complex problems":
                st.info("You seem to be an **Analytical Thinker**! We'll recommend roles in analysis and R&D.")
            elif q2 == "Creative and artistic tasks":
                st.info("You seem to be a **Creative Type**! We'll recommend roles in design and marketing.")
            else:
                st.info("You seem to be an **Organizer**! We'll recommend roles in management and operations.")

def show_resume_builder():
    """
    A mocked-up page for the resume builder. (Request #7)
    """
    st.header("📄 Resume Builder")
    st.markdown("Enter your details to generate a role-specific resume.")
    
    # --- NEW: Resume Type Selector ---
    resume_type = st.radio("1. Select Resume Type", ("Technical", "Managerial", "Creative"), horizontal=True)
    
    with st.form("resume_form"):
        st.subheader("2. Personal Details")
        col1, col2 = st.columns(2)
        col1.text_input("Full Name")
        col2.text_input("Email")
        st.text_input("Phone Number")
        st.text_area("Professional Summary")
        
        # --- NEW: Detailed Education ---
        st.subheader("3. Education")
        col1, col2 = st.columns(2)
        col1.text_input("Degree (e.g., B.Tech Computer Science)")
        col2.text_input("College/University")
        col1.text_input("Year of Completion (e.g., 2025)")
        col2.text_input("Marks/CGPA (e.g., 8.5)")
        
        # --- NEW: Multiple Projects with Tags ---
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
        st.text_area("Internship/Work Experience", placeholder="Describe your experience...")
        
        submitted = st.form_submit_button("Generate Resume", use_container_width=True, type="primary")
        
        if submitted:
            st.success(f"Generating your '{resume_type}' resume!")
            st.info("Based on your selection, we would highlight projects with 'Technical' tags.")
            st.download_button(
                label="Download Resume as PDF (Mock)",
                data="This is a mock PDF.",
                file_name=f"mock_{resume_type}_resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# --- NEW: Personal Settings Page (Request #5) ---
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

# --- NEW: Application Management Page (Request #3, 4, 5) ---
def show_manage_applications():
    """
    A new page to manage applicants for a specific job.
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
        st.divider()
        col1, col2, col3 = st.columns([2, 1, 1.5])
        
        with col1:
            st.subheader(applicant['name'])
            st.caption(f"Skills: {applicant['skills']}")
        
        with col2:
            # --- NEW: View Profile Button (Request #4) ---
            if st.button("View Profile (Mock)", key=f"view_{applicant['id']}", use_container_width=True):
                # This fixes the "takes me back" bug by showing a modal instead (Request #3)
                with st.dialog("Mock Profile View"):
                    st.header(f"Profile: {applicant['name']}")
                    st.markdown(f"**Email:** {applicant['name'].lower().replace(' ','_')}@email.com")
                    st.markdown(f"**Skills:** {applicant['skills']}")
                    st.bar_chart({"Profile Match": 75})
                    st.info("This is a mock profile view.")
                    if st.button("Close", use_container_width=True):
                        st.rerun()

        with col3:
            # --- NEW: Stateful Buttons (Request #5) ---
            status = applicant['status']
            
            if status == "Pending":
                c1, c2 = st.columns(2)
                if c1.button("Shortlist", key=f"short_{applicant['id']}", use_container_width=True, type="primary"):
                    applicant['status'] = "Shortlisted"
                    st.rerun()
                if c2.button("Reject", key=f"rej_{applicant['id']}", use_container_width=True):
                    applicant['status'] = "Rejected"
                    st.rerun()
            
            elif status == "Shortlisted":
                st.success("✅ Added to shortlist")
            
            elif status == "Rejected":
                st.error("❌ Rejected for now")

def show_recruiter_dashboard():
    """
    A mocked-up dashboard for recruiters.
    """
    # --- NEW: Page routing logic (Request #3) ---
    # If a job has been selected, show the manage page instead
    if 'view_job' in st.session_state and st.session_state.view_job:
        show_manage_applications()
        return
        
    st.header("📈 Recruiter Dashboard")
    st.markdown("Manage your internship postings and view matched candidates.")
    
    # --- NEW: Recruiter K-Cards (Request #1) ---
    st.subheader("Live Stats (Mock)")
    col1, col2, col3 = st.columns(3)
    col1.container(border=True).metric("Posted Internships", "3")
    col2.container(border=True).metric("Total Applicants", "96")
    col3.container(border=True).metric("Top Matches", "24")

    st.divider()
    
    with st.container(border=True):
        st.subheader("Your Posted Internships")
        
        # --- NEW: Clickable buttons (Request #3) ---
        mock_jobs = {
            "Web Developer Intern": "(32 Applicants, 8 Matches)",
            "Data Analyst Intern": "(19 Applicants, 4 Matches)",
            "UI/UX Designer": "(45 Applicants, 12 Matches)"
        }
        
        for job_title, stats in mock_jobs.items():
            # When button is clicked, it sets the session state and reruns
            if st.button(f"**{job_title}** {stats}", use_container_width=True, help=f"Click to manage applicants for {job_title}"):
                st.session_state.view_job = job_title
                st.rerun()


def show_post_internship_form():
    """
    A mocked-up form for recruiters to post internships.
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
    A mocked-up page for searching candidates.
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
    The main landing page with login/register forms.
    This is a *simulated* login, not a real one.
    
    --- THIS FUNCTION HAS BEEN REDESIGNED ---
    """
    st.title("Welcome to the Internship Recommendation Platform")
    st.markdown("Bridging the gap between learning and your future career.")
    
    # Use a container to center the login box
    with st.container(border=True):
        # 1. Central "I am a:" toggle
        user_type = st.radio(
            "Are you a:",
            ("Student", "Recruiter"),
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # 2. Tabs for "Login" and "Register"
        login_tab, register_tab = st.tabs(["Login", "Register"])
        
        with login_tab:
            st.subheader("Login")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if login_user and login_pass:
                    # SIMULATE LOGIN
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type  # Use the central toggle
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
                    st.session_state.user_type = user_type # Use the central toggle
                    st.session_state.username = reg_user
                    st.rerun()

# --- MAIN APPLICATION LOGIC ---

def main():
    """
    The main function that controls the app's flow.
    """
    # Initialize session state variables if they don't exist
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'username' not in st.session_state:
        st.session_state.username = ""
    # --- NEW: Initialize api_data in session state ---
    if 'api_data' not in st.session_state:
        st.session_state.api_data = {
            "recommendations": [],
            "student_skills": [],
            "skill_gap": []
        }
    
    # --- NEW: Initialize mock data for recruiters ---
    if 'view_job' not in st.session_state:
        st.session_state.view_job = None
    
    if 'mock_applicants' not in st.session_state:
        # We need to re-initialize this every time in this mock setup
        # or use a more advanced session state key to check for reset.
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
        # A simple flag to "reset" the applicant status on a full page reload/login
        # This is a hack for Streamlit's statefulness
        for job in st.session_state.mock_applicants:
            for app in st.session_state.mock_applicants[job]:
                app['status'] = "Pending"


    # Check if the user is logged in
    if st.session_state.logged_in:
        # --- LOGGED-IN VIEW (Sidebar Navigation) ---
        st.sidebar.header(f"Welcome, {st.session_state.username}!")
        st.sidebar.markdown(f"**Role:** {st.session_state.user_type}")
        
        if st.session_state.user_type == "Student":
            student_pages = {
                "My Dashboard": show_student_dashboard,
                "Psychometric Test": show_psychometric_test,
                "Resume Builder": show_resume_builder,
                "Personal Settings": show_personal_settings, # --- NEW PAGE ADDED ---
            }
            page_choice = st.sidebar.radio("Navigation", options=student_pages.keys())
            # Call the selected page function
            student_pages[page_choice]()
            
        elif st.session_state.user_type == "Recruiter":
            recruiter_pages = {
                "My Dashboard": show_recruiter_dashboard,
                "Post New Internship": show_post_internship_form,
                "Search Candidates": show_candidate_search,
            }
            page_choice = st.sidebar.radio("Navigation", options=recruiter_pages.keys())
            # --- THIS IS THE CORRECTED LINE (Line 620) ---
            recruiter_pages[page_choice]()
        
        # --- NEW: Sidebar collapse hint (Request #2) ---
        st.sidebar.caption("Tip: You can collapse this panel by clicking the 'X' at the top.")
        
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.username = ""
            st.session_state.view_job = None # Reset recruiter view
            # --- NEW: Clear API data on logout ---
            st.session_state.api_data = {"recommendations": [], "student_skills": [], "skill_gap": []}
            st.rerun()

    else:
        # --- LOGGED-OUT VIEW (Landing Page) ---
        show_landing_page()

if __name__ == "__main__":
    main()

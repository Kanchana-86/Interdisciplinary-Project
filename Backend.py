import streamlit as st
import pandas as pd

# --- Data Loading & Processing Logic ---
EXCEL_PATH = r"C:\Users\kanch\Downloads\Interdisiplinary Project\LinkedIn_Internships_Dataset.xlsx"

@st.cache_data  # Cache the data so it only loads once
def load_data():
    """
    Loads the full DataFrame and pre-processes it.
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

def get_recommendations_from_dataframe(selected_courses, df, all_skills):
    """
    This function generates recommendations based on selected courses.
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

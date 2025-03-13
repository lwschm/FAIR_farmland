import streamlit as st

# ✅ Set the page configuration FIRST before anything else
st.set_page_config(page_title="FAIR Evaluation App", page_icon="🌐", layout="wide")

# Define pages
page1 = st.Page("pages/fair_evaluation.py", title="FAIR Evaluation", icon="📊", default=True)
page2 = st.Page("pages/sparql_explorer.py", title="SPARQL Explorer", icon="🔍")
page3 = st.Page("pages/about.py", title="About", icon="ℹ️")

# GitHub Repository Link in Sidebar
repo_url = "https://github.com/fairagro/FAIR_evaluation_repository"
st.sidebar.markdown(f'<a href="{repo_url}" target="_blank" style="text-decoration: none; font-weight: bold;">🔗 GitHub Repository</a>', unsafe_allow_html=True)

# Configure navigation
pg = st.navigation([page1, page2, page3])

# Run the selected page
pg.run()

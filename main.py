import streamlit as st

# ✅ Set the page configuration FIRST before anything else
st.set_page_config(page_title="FAIR Evaluation App", page_icon="🌐", layout="wide")

# Define pages
page1 = st.Page("pages/fair_evaluation.py", title="FAIR Evaluation", icon="📊", default=True)
page2 = st.Page("pages/sparql_explorer.py", title="SPARQL Explorer", icon="🔍")

# Configure navigation
pg = st.navigation([page1, page2])

# Run the selected page
pg.run()

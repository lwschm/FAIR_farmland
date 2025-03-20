import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from query_templates import FAIR_QUERIES, BONARES_QUERIES  # Import query templates
from dotenv import load_dotenv
import os

load_dotenv()

fuseki_base_url = os.getenv("FUSEKI_BASE_URL")

endpoints = {
    "FAIR_Metrics": f"{fuseki_base_url}/FAIR_Metrics/sparql",
    "BonaRes": f"{fuseki_base_url}/bonares/sparql"
}

# ✅ Dropdown for selecting the endpoint
selected_endpoint = st.selectbox("Select SPARQL Endpoint:", list(endpoints.keys()))

# ✅ Load correct query templates based on the selected endpoint
template_queries = FAIR_QUERIES if selected_endpoint == "FAIR" else BONARES_QUERIES

# Use the selected endpoint for queries
SPARQL_ENDPOINT = endpoints[selected_endpoint]

# Function to execute SPARQL queries
def execute_sparql_query(query):
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    cols = results["head"]["vars"]
    rows = [
        {col: result.get(col, {}).get("value", None) for col in cols}
        for result in results["results"]["bindings"]
    ]
    return pd.DataFrame(rows, columns=cols)


st.title("SPARQL Explorer")
st.write(f"Querying endpoint: {SPARQL_ENDPOINT}")

# ✅ Dropdown menu for selecting a template query
template_names = list(template_queries.keys())
selected_template = st.selectbox("Choose a template query:", template_names)

# Retrieve the selected template query
default_query = template_queries[selected_template]

# ✅ Full-width query input box
user_query = st.text_area("Enter your SPARQL query here:", value=default_query, height=500)

# ✅ Initialize session state for query results & page number
if "query_results" not in st.session_state:
    st.session_state.query_results = None  # Stores DataFrame
if "page_number" not in st.session_state:
    st.session_state.page_number = 1  # Stores current page

if st.button("Execute Query"):
    if user_query.strip():
        try:
            # ✅ Run the query and store results in session state
            st.session_state.query_results = execute_sparql_query(user_query)
            st.session_state.page_number = 1  # Reset to first page on new query

        except Exception as e:
            st.error(f"An error occurred: {e}")

# ✅ Display query results if available
if st.session_state.query_results is not None:
    df = st.session_state.query_results
    total_rows = len(df)
    rows_per_page = 500  # Adjust as needed

    if total_rows > rows_per_page:
        # ✅ Page selector, persistent with session state
        max_pages = (total_rows // rows_per_page) + 1
        st.session_state.page_number = st.number_input(
            "Page number", min_value=1, max_value=max_pages, value=st.session_state.page_number, step=1
        )

        # ✅ Paginate results
        start_row = (st.session_state.page_number - 1) * rows_per_page
        end_row = start_row + rows_per_page
        df_paginated = df.iloc[start_row:end_row]

        st.dataframe(df_paginated, use_container_width=True)
    else:
        # ✅ Display full results if small
        st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")

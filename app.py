import streamlit as st  # Streamlit for UI rendering
from datetime import datetime  # For tracking start and end times
import plotly.graph_objects as go  # For creating grouped bar charts
from FES_evaluation import fes_evaluate_to_list, fes_evaluation_result_example  # Cached FES evaluation results
from doi_to_dqv import create_dqv_representation  # Function to generate RDF representation
from rdf_utils import extract_scores_from_rdf  # Utility to extract scores from RDF
from pyvis.network import Network  # For RDF graph visualization
import streamlit.components.v1 as components  # To embed HTML in Streamlit
from FUJI_evaluation import fuji_evaluation_result_example  # Cached FUJI evaluation results

# Example FES and FUJI evaluation results
fes_evaluation_result = fes_evaluation_result_example
fuji_evaluation_result = fuji_evaluation_result_example

# Streamlit UI
st.title("DOI to FAIR Evaluation")

# Development toggle
development_mode = st.checkbox("Use cached result (Development Mode)", value=True)

# Input field for DOI
data_doi = st.text_input("Enter a DOI:", placeholder="10.1000/xyz123")

# Provide a default DOI in developer mode if no input is provided
if development_mode and not data_doi:
    st.warning("Using default DOI for development mode.")
    data_doi = "10.1000/xyz123"

# Initialize session state for RDF representation and visualization toggle
if "dqv_representation" not in st.session_state:
    st.session_state["dqv_representation"] = None
if "show_rdf" not in st.session_state:
    st.session_state["show_rdf"] = False

# Generate FAIR Evaluation button
if st.button("Generate FAIR Evaluation"):
    if data_doi or development_mode:
        if development_mode:
            st.warning("Using cached result for development.")
            fes_evaluation_result_used = fes_evaluation_result
        else:
            fes_evaluation_result_used = fes_evaluate_to_list(data_doi)

        if fes_evaluation_result_used:
            start_time = datetime.now()
            end_time = datetime.now()

            try:
                dqv_representation = create_dqv_representation(
                    doi=data_doi,
                    fes_evaluation_result=fes_evaluation_result_used,
                    fuji_evaluation_result=fuji_evaluation_result,
                    start_time=start_time,
                    end_time=end_time,
                )

                # Save RDF graph to session state for visualization
                st.session_state["dqv_representation"] = dqv_representation

                scores_by_metric = extract_scores_from_rdf(dqv_representation)

                fes_scores = scores_by_metric.get("fes", {})
                fuji_scores = scores_by_metric.get("fuji", {})

                dimensions = ["Findability", "Accessibility", "Interoperability", "Reusability"]

                fes_values = [
                    fes_scores.get("findability_score", 0),
                    fes_scores.get("accessibility_score", 0),
                    fes_scores.get("interoperability_score", 0),
                    fes_scores.get("reusability_score", 0),
                ]

                fuji_values = [
                    fuji_scores.get("findability_score", 0),
                    fuji_scores.get("accessibility_score", 0),
                    fuji_scores.get("interoperability_score", 0),
                    fuji_scores.get("reusability_score", 0),
                ]

                # Create a grouped bar chart with Plotly
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=dimensions,
                    y=fes_values,
                    name="FES",
                    marker={"color": "skyblue"}  # Use marker dictionary for color
                ))
                fig.add_trace(go.Bar(
                    x=dimensions,
                    y=fuji_values,
                    name="FUJI",
                    marker={"color": "orange"}  # Use marker dictionary for color
                ))

                # Update layout for grouped bars
                fig.update_layout(
                    title="FAIR Dimension Scores (Grouped by FES and FUJI)",
                    xaxis_title="FAIR Dimensions",
                    yaxis_title="Scores",
                    barmode="group",  # Group the bars side by side
                    legend_title="Source"
                )

                # Save the bar chart figure to session state
                st.session_state["bar_chart"] = fig

            except Exception as e:
                st.error(f"Failed to process RDF representation: {e}")
        else:
            st.error("No FES scores returned.")
    else:
        st.warning("Please enter a DOI.")

# Always display the grouped bar chart
if "bar_chart" in st.session_state:
    st.plotly_chart(st.session_state["bar_chart"])

# Button to toggle RDF graph visualization
if st.session_state["dqv_representation"] is not None:
    if st.button("Visualize RDF Graph"):
        st.session_state["show_rdf"] = not st.session_state["show_rdf"]

    # Conditionally render the RDF graph below the bar chart
    if st.session_state["show_rdf"]:
        rdf_graph = st.session_state["dqv_representation"]
        net = Network(height="500px", width="100%", notebook=True)

        # Add nodes and edges to the Pyvis graph
        for subj, pred, obj in rdf_graph:
            net.add_node(str(subj), label=str(subj), color="blue")
            net.add_node(str(obj), label=str(obj), color="green")
            net.add_edge(str(subj), str(obj), title=str(pred))

        # Save the Pyvis graph to an HTML file and display it in Streamlit
        net.save_graph("rdf_graph.html")
        st.subheader("RDF Graph Visualization")
        components.html(open("rdf_graph.html", "r").read(), height=500)

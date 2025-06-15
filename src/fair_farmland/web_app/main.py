import streamlit as st
import os
import json
from pathlib import Path
import tempfile
from .pdf_processor import pdf_to_markdown
from .metadata_extractor import extract_metadata

# Page configuration
st.set_page_config(
    page_title="Farmland Data Metadata Extractor",
    page_icon="🌾",
    layout="wide"
)

st.title("Farmland Data Metadata Extractor")
st.markdown("""
This application extracts metadata about farmland data from scientific publications.
Upload a PDF to get started.
""")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing PDF..."):
        # Convert PDF to markdown
        markdown_text = pdf_to_markdown(uploaded_file)
        
        # Extract metadata using OpenAI
        metadata = extract_metadata(markdown_text)
        
        # Check if we got real metadata or an error placeholder
        if metadata["metadata"]["title"] == "API key missing":
            st.error("OpenAI API key is required to extract metadata. Please enter it in the sidebar.")
            st.stop()
    
    st.success("Metadata extracted successfully!")
    
    # Display metadata in a structured format
    st.subheader("Publication Metadata")
    meta = metadata["metadata"]
    st.write(f"**Title:** {meta['title']}")
    st.write(f"**Authors:** {', '.join(meta['authors'])}")
    st.write(f"**Journal:** {meta['journal']}")
    st.write(f"**Year:** {meta['year']}")
    st.write(f"**DOI:** {meta['doi']}")
    
    # Display data sources
    st.subheader("Farmland Data Sources")
    for i, source in enumerate(metadata["data_sources"]):
        with st.expander(f"🌾 {source['source_name']}"):
            st.write(f"**Description:** {source['description']}")
            st.write(f"**Location:** {source['country']}, {source['region']}")
            st.write(f"**Time Period:** {source['earliest_year']} - {source['latest_year']}")
            st.write(f"**Transaction Types:** {', '.join(source['transaction_types'])}")
            st.write(f"**Spatial Resolution:** {source['spatial_resolution']}")
            st.write(f"**Accessibility:** {source['accessibility']}")
            st.write(f"**Number of Observations:** {source['number_of_observations']}")
            st.write(f"**Data Format:** {source['data_format']}")
            if source['url']:
                st.write(f"**URL:** [{source['url']}]({source['url']})")
    
    # Download options
    st.subheader("Download Options")
    
    # Download raw metadata as JSON
    st.download_button(
        label="Download Metadata (JSON)",
        data=json.dumps(metadata, indent=2),
        file_name=f"{Path(uploaded_file.name).stem}_metadata.json",
        mime="application/json"
    )
    
    # FAIR Assessment
    st.subheader("FAIR Assessment")
    
    # Get assessment scores from metadata
    assessment = metadata.get("assessment", {})
    findable_score = int(assessment.get("findability", 0) * 100)
    accessible_score = int(assessment.get("accessibility", 0) * 100)
    interoperable_score = int(assessment.get("interoperability", 0) * 100)
    reusable_score = int(assessment.get("reusability", 0) * 100)
    
    # Calculate overall score
    overall_score = (findable_score + accessible_score + interoperable_score + reusable_score) // 4
    
    # Display scores
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Findable", f"{findable_score}%")
    col2.metric("Accessible", f"{accessible_score}%")
    col3.metric("Interoperable", f"{interoperable_score}%")
    col4.metric("Reusable", f"{reusable_score}%")
    col5.metric("Overall", f"{overall_score}%")
    
    # Display assessment reasons
    st.markdown("### Assessment Details")
    st.markdown(f"**Findability:** {assessment.get('findability_reason', 'No reason provided')}")
    st.markdown(f"**Accessibility:** {assessment.get('accessibility_reason', 'No reason provided')}")
    st.markdown(f"**Interoperability:** {assessment.get('interoperability_reason', 'No reason provided')}")
    st.markdown(f"**Reusability:** {assessment.get('reusability_reason', 'No reason provided')}")
    
    # Add some explanation
    st.markdown("""
    ### About FAIR Assessment
    
    This FAIR (Findable, Accessible, Interoperable, Reusable) assessment is based on:
    
    - **Findable**: Presence of DOI, metadata richness, and proper identification
    - **Accessible**: Availability of URL, accessibility information, and access protocols
    - **Interoperable**: Use of standard formats, vocabularies, and metadata standards
    - **Reusable**: Details about licenses, provenance, and metadata completeness
    
    For a more detailed FAIR assessment, consider using specialized tools like F-UJI or FES.
    """) 
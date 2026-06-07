"""
Streamlit UI for IT Ticket Agent System
"""
import streamlit as st
from Agents.classifier import ClassifierAgent
from Agents.router import RouterAgent
from Agents.resolver import ResolverAgent
from Agents.supervisor import SupervisorAgent

# Page configuration
st.set_page_config(
    page_title="IT Ticket Agent System",
    page_icon="🎫",
    layout="wide"
)

# Title and description
st.title("🎫 IT Ticket Agent System")
st.markdown("### Multi-Agent Workflow for IT Support Ticket Resolution")
st.markdown("---")

# Initialize agents
@st.cache_resource
def get_agents():
    return {
        'classifier': ClassifierAgent(),
        'router': RouterAgent(),
        'resolver': ResolverAgent(),
        'supervisor': SupervisorAgent()
    }

agents = get_agents()

# Session state initialization
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'results' not in st.session_state:
    st.session_state.results = None

# Ticket input form
with st.form("ticket_form"):
    st.subheader("📝 Submit IT Support Ticket")

    ticket_description = st.text_area(
        "Describe the IT issue you're experiencing:",
        placeholder="e.g., My printer is not working and showing error code 0x00000709",
        height=100
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        urgency = st.selectbox(
            "Urgency Level:",
            options=["Low", "Medium", "High", "Critical"],
            index=2  # Default to Medium
        )

    with col2:
        st.write("")  # Spacer
        submit_button = st.form_submit_button(
            "🚀 Process Ticket",
            type="primary",
            use_container_width=True
        )

# Process ticket when submitted
if submit_button and ticket_description.strip():
    st.session_state.processing = True
    st.session_state.results = None

    # Create progress containers
    progress_container = st.container()
    results_container = st.container()

    with progress_container:
        st.subheader("⚙️ Processing Ticket Through Agent Workflow")

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Classification
        status_text.text("Step 1/4: Classifying ticket...")
        progress_bar.progress(25)
        classification = agents['classifier'].classify(ticket_description)

        # Step 2: Routing
        status_text.text("Step 2/4: Routing to appropriate department...")
        progress_bar.progress(50)
        routing = agents['router'].route(classification, urgency)

        # Step 3: Resolution
        status_text.text("Step 3/4: Generating resolution steps...")
        progress_bar.progress(75)
        resolution = agents['resolver'].resolve(classification, ticket_description)

        # Step 4: Supervision
        status_text.text("Step 4/4: Final review and confidence assessment...")
        progress_bar.progress(100)
        results = agents['supervisor'].supervise(classification, routing, resolution)

        status_text.text("✅ Processing complete!")
        progress_bar.progress(100)

        # Store results
        st.session_state.results = results
        st.session_state.processing = False

# Display results
if st.session_state.results and not st.session_state.processing:
    results = st.session_state.results

    with results_container:
        st.subheader("📊 Ticket Processing Results")

        # Confidence and escalation info
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            confidence = results['confidence']
            if confidence >= 0.75:
                st.success(f"🎯 Confidence Score: {confidence:.0%}")
            elif confidence >= 0.5:
                st.warning(f"⚠️ Confidence Score: {confidence:.0%}")
            else:
                st.error(f"❌ Confidence Score: {confidence:.0%}")

        with col2:
            if results['escalate']:
                st.error("🚨 **ESCALATION REQUIRED**")
            else:
                st.info("✅ Auto-resolution possible")

        with col3:
            st.metric("SLA Hours", f"{results['sla_hours']}h")

        # Escalation reason if applicable
        if results['escalate']:
            st.error(f"**Reason:** {results['escalation_reason']}")

        # Ticket details in expandable sections
        with st.expander("🔍 Classification Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Category:** {results['category']}")
                st.write(f"**Subcategory:** {results['subcategory']}")
            with col2:
                st.write(f"**Priority:** {results['priority']}")
                st.write(f"**Department:** {results['department']}")
                st.write(f"**Team:** {results['team']}")
            st.caption(f"*{results['classifier_notes']}*")

        with st.expander("🛠️ Resolution Steps", expanded=True):
            st.write(f"**Estimated Resolution Time:** {results['estimated_time']}")
            st.write("**Recommended Actions:**")
            for i, step in enumerate(results['resolution_steps'], 1):
                st.write(f"{i}. {step}")

        with st.expander("📋 Processing Notes", expanded=False):
            st.write(f"**Router Notes:** {results['router_notes']}")
            st.write(f"**Supervisor Notes:** {results['supervisor_notes']}")

            if results['similar_tickets']:
                st.write("**Similar Past Tickets:**")
                for ticket in results['similar_tickets']:
                    st.write(f"• {ticket}")

        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("📋 New Ticket", type="secondary"):
                st.session_state.processing = False
                st.session_state.results = None
                st.rerun()

        with col2:
            if st.button("📄 Export Results", type="secondary"):
                # Create exportable text
                export_text = f"""
IT Ticket Processing Results
===========================
Ticket Description: {ticket_description}
Category: {results['category']}
Subcategory: {results['subcategory']}
Department: {results['department']}
Team: {results['team']}
Priority: {results['priority']}
Confidence: {confidence:.0%}
Escalation Required: {'Yes' if results['escalate'] else 'No'}
Escalation Reason: {results['escalation_reason']}
Estimated Resolution Time: {results['estimated_time']}
SLA Hours: {results['sla_hours']}h

Resolution Steps:
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(results['resolution_steps'])])}

Processing Notes:
- Router: {results['router_notes']}
- Supervisor: {results['supervisor_notes']}
                """
                st.download_button(
                    label="💾 Download Results",
                    data=export_text,
                    file_name="ticket_results.txt",
                    mime="text/plain"
                )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "IT Ticket Agent System • Powered by CrewAI & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
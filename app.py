"""
Main Streamlit Application for IT Ticket Routing System
"""
import streamlit as st
import json
from datetime import datetime
from agents.classifier import ClassifierAgent
from agents.router import RouterAgent
from agents.resolver import ResolverAgent
from agents.supervisor import SupervisorAgent


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "tickets" not in st.session_state:
        st.session_state.tickets = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def display_header():
    """Display application header"""
    st.set_page_config(page_title="IT Ticket Router", layout="wide")
    st.title("🎫 Intelligent IT Ticket Routing System")
    st.markdown("**Agent Titans** | NASSCOM Agentic AI Hackathon 2026")
    st.markdown("---")


def display_ticket_submission():
    """Display ticket submission form"""
    st.header("📝 Submit IT Ticket")
    
    with st.form("ticket_form"):
        ticket_description = st.text_area(
            "Ticket Description",
            placeholder="Describe the IT issue...",
            height=150
        )
        
        reporter_name = st.text_input("Reporter Name", placeholder="Your name")
        reporter_email = st.text_input("Email", placeholder="your.email@company.com")
        
        col1, col2 = st.columns(2)
        with col1:
            user_department = st.selectbox(
                "Your Department",
                ["Sales", "Engineering", "HR", "Finance", "Operations", "Other"]
            )
        with col2:
            urgency = st.selectbox(
                "Perceived Urgency",
                ["Low", "Medium", "High", "Critical"]
            )
        
        submit_button = st.form_submit_button("🚀 Process Ticket")
        
        if submit_button:
            if ticket_description.strip():
                process_ticket(
                    ticket_description,
                    reporter_name,
                    reporter_email,
                    user_department,
                    urgency
                )
            else:
                st.error("Please enter a ticket description.")


def process_ticket(description, name, email, dept, urgency):
    """Process ticket through multi-agent system"""
    st.header("⚙️ Processing Ticket...")
    
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    try:
        # Step 1: Classification
        status_placeholder.info("🤖 Step 1/4: Analyzing ticket category...")
        progress_bar.progress(25)
        classifier = ClassifierAgent()
        classification = classifier.classify(description)
        
        # Step 2: Routing
        status_placeholder.info("🤖 Step 2/4: Determining department and priority...")
        progress_bar.progress(50)
        router = RouterAgent()
        routing = router.route(classification, urgency)
        
        # Step 3: Resolution
        status_placeholder.info("🤖 Step 3/4: Generating resolution steps...")
        progress_bar.progress(75)
        resolver = ResolverAgent()
        resolution = resolver.resolve(classification, description)
        
        # Step 4: Supervision
        status_placeholder.info("🤖 Step 4/4: Final review and confidence assessment...")
        progress_bar.progress(90)
        supervisor = SupervisorAgent()
        final_result = supervisor.supervise(
            classification, routing, resolution
        )
        progress_bar.progress(100)
        
        st.session_state.last_result = final_result
        st.success("✅ Ticket processed successfully!")
        
        # Store ticket
        st.session_state.tickets.append({
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "reporter": name,
            "email": email,
            "result": final_result
        })
        
        display_results(final_result)
        
    except Exception as e:
        st.error(f"❌ Error processing ticket: {str(e)}")


def display_results(result):
    """Display ticket processing results"""
    st.header("📊 Ticket Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Category", result.get("category", "N/A"))
    with col2:
        st.metric("Priority", result.get("priority", "N/A"))
    with col3:
        confidence = result.get("confidence", 0)
        st.metric("Confidence", f"{confidence:.0%}")
    with col4:
        escalation = "Yes" if result.get("escalate", False) else "No"
        st.metric("Escalate?", escalation)
    
    st.markdown("---")
    
    # Department & Team Info
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏢 Department Assignment")
        st.write(f"**Department:** {result.get('department', 'N/A')}")
        st.write(f"**Team:** {result.get('team', 'N/A')}")
    
    with col2:
        st.subheader("📋 Classification Details")
        st.write(f"**Main Category:** {result.get('category', 'N/A')}")
        st.write(f"**Sub-Category:** {result.get('subcategory', 'N/A')}")
    
    st.markdown("---")
    
    # Resolution Steps
    st.subheader("✅ Recommended Resolution Steps")
    steps = result.get("resolution_steps", [])
    if steps:
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step}")
    else:
        st.info("No specific resolution steps available. Escalation recommended.")
    
    st.markdown("---")
    
    # Reasoning & Explanation
    with st.expander("🔍 Agent Reasoning & Explanation"):
        st.write("**Classifier Analysis:**")
        st.write(result.get("classifier_notes", "N/A"))
        
        st.write("\n**Router Reasoning:**")
        st.write(result.get("router_notes", "N/A"))
        
        st.write("\n**Supervisor Assessment:**")
        st.write(result.get("supervisor_notes", "N/A"))
    
    # Escalation Reason (if applicable)
    if result.get("escalate"):
        st.warning(f"⚠️ **Escalation Reason:** {result.get('escalation_reason', 'Review needed')}")
    
    # Similar Past Tickets
    with st.expander("📚 Similar Past Tickets (RAG)"):
        similar = result.get("similar_tickets", [])
        if similar:
            for ticket in similar:
                st.write(f"- {ticket}")
        else:
            st.info("No similar tickets found in knowledge base.")


def display_history():
    """Display ticket history"""
    st.header("📜 Ticket History")
    
    if st.session_state.tickets:
        for i, ticket in enumerate(reversed(st.session_state.tickets), 1):
            with st.expander(f"Ticket #{i} - {ticket['timestamp'][:10]}"):
                st.write(f"**Reporter:** {ticket['reporter']} ({ticket['email']})")
                st.write(f"**Description:** {ticket['description'][:100]}...")
                if ticket['result']:
                    st.write(f"**Category:** {ticket['result'].get('category', 'N/A')}")
                    st.write(f"**Confidence:** {ticket['result'].get('confidence', 0):.0%}")
    else:
        st.info("No tickets processed yet.")


def main():
    """Main application flow"""
    initialize_session_state()
    display_header()
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["Submit Ticket", "History"])
    
    with tab1:
        display_ticket_submission()
    
    with tab2:
        display_history()


if __name__ == "__main__":
    main()

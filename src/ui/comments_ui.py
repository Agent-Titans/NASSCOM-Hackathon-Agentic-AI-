"""Ticket comment thread — requester and assignee collaboration."""
from __future__ import annotations

import html

import streamlit as st

from src.db.models import User
from src.stores.comment_store import CommentStore
from src.ui.ticket_display import person_name


def render_ticket_comments(
    session,
    ticket_id: str,
    user: User,
    wrap_fn,
    key_prefix: str,
) -> None:
    store = CommentStore(session)
    comments = store.list_for_ticket(ticket_id)

    if comments:
        items = []
        for c in comments:
            author = session.get(User, c.user_id)
            name = person_name(author.email) if author else "User"
            role_lbl = "Agent" if c.author_role == "assignee" else "Employee"
            ts = c.created_at.strftime("%b %d, %Y %H:%M")
            items.append(
                f'<div class="ticket-comment">'
                f'<p class="ticket-comment-meta">'
                f'<strong>{html.escape(name)}</strong> · {html.escape(role_lbl)} · '
                f'{html.escape(ts)}</p>'
                f'<p class="ticket-comment-body">{html.escape(c.body)}</p>'
                f"</div>"
            )
        st.markdown(
            wrap_fn(
                '<div class="itsm-section"><p class="itsm-section-title">Comments</p>'
                + "".join(items)
                + "</div>"
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            wrap_fn(
                '<div class="itsm-section"><p class="itsm-section-title">Comments</p>'
                '<p class="ticket-comment-empty">No comments yet.</p></div>'
            ),
            unsafe_allow_html=True,
        )

    with st.form(f"{key_prefix}_comment_form", border=False):
        body = st.text_area(
            "Add a comment",
            placeholder="Add an update or question for the team…",
            height=90,
            label_visibility="collapsed",
        )
        if st.form_submit_button("Post comment", type="primary"):
            if not body.strip():
                st.error("Comment cannot be empty.")
            else:
                store.add(ticket_id, user, body.strip())
                st.rerun()

from src.db.session import init_db, get_session_factory
from src.db.models import User, Ticket
from sqlalchemy import select

init_db()
Session=get_session_factory()
with Session() as s:
    users=s.execute(select(User).order_by(User.email)).scalars().all()
    print('USERS', len(users))
    for u in users[:20]:
        print(u.email, u.role, u.department)
    tickets=s.execute(select(Ticket).order_by(Ticket.created_at.desc())).scalars().all()
    print('TICKETS', len(tickets))
    for t in tickets[:10]:
        print(t.ticket_id, t.title[:40], t.hand, t.status, t.department_queue, t.priority, t.created_at)

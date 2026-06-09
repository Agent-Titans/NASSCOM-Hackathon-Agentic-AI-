import os
import time
from datetime import datetime

os.environ['GOOGLE_API_KEY'] = ''
os.environ['SQLITE_DATABASE_URL'] = 'sqlite:///./tmp/test_app.db'

from src.db.session import init_db, get_session_factory
from src.db.models import Ticket, User
from src.services.ticket_service import TicketService

init_db()
Session = get_session_factory()
with Session() as session:
    user = session.query(User).filter(User.email == 'synthetic@demo.local').one_or_none()
    if user is None:
        user = User(email='synthetic@demo.local', role='requester')
        session.add(user)
        session.commit()
        session.refresh(user)

    session.query(Ticket).filter(Ticket.ticket_id.like('SYN-%')).delete(synchronize_session=False)
    session.query(Ticket).filter(Ticket.ticket_id.like('RAG-%')).delete(synchronize_session=False)
    session.commit()

    cat_to_dept = {
        'Security': 'SecOps',
        'Access Management': 'Identity',
        'Infrastructure': 'Hardware',
        'Application': 'Software',
        'Database': 'DBA',
        'Storage': 'Storage',
        'Network': 'Network',
    }
    templates = {
        'Security': [
            'I found a public AWS secret key in a GitHub repo and need it revoked immediately.',
            'There is a ransomware warning on my workstation and files are being encrypted.',
            'Suspicious login attempts show credential stuffing against our corporate portal.',
            'A phishing email with a malicious attachment bypassed our filters.',
            'My account was compromised with unauthorized access to confidential data.',
            'I see malware alerts from the endpoint detection system on several hosts.',
            'The security team flagged an exposed customer database leak in S3.',
            'There is a brute-force attack on the VPN gateway from an unknown IP.',
            'A critical audit log deletion event was reported from the SecOps console.',
            'Our identity provider reported a suspected credential compromise incident.',
            'A public repo contains secret keys and tokens that must be rotated.',
            'Someone is using a stolen session token to access privileged systems.',
            'Sensitive files were copied off the server during an unauthorized session.',
            'The firewall logged a suspicious data exfiltration pattern.',
            'I received a notification of an exposed API key in source control.',
        ],
        'Access Management': [
            'I cannot login to the corporate portal because my password was expired.',
            'My Windows account is locked and I need a password reset link.',
            'MFA is failing for my account and I cannot access the VPN.',
            'I need access to the HR system but my user is not authorized.',
            'Please unlock my Active Directory account and reset my corporate password.',
            'I lost my token device and cannot complete multi-factor authentication.',
            'The identity provider denies my login with unknown credential errors.',
            'I need temporary access to the finance dashboard for an audit review.',
            'My permission request is pending and I cannot access the identity portal.',
            'I am unable to reset my password through self-service and need help.',
            'My account is stuck in locked state after too many bad password attempts.',
            'The SSO login redirects to an error page when I try to enter the app.',
            'I need role-based access to the internal CRM for sales support.',
            'The access request portal is not granting me the correct identity permissions.',
            'I am requesting privilege escalation to view sensitive documents.',
        ],
        'Infrastructure': [
            'Docker Desktop fails to start with a hypervisor and BIOS virtualization error.',
            'My laptop shows a hardware-assisted virtualization issue after firmware update.',
            'The server RAID controller reports a degraded disk array and needs replacement.',
            'The workstation power supply is failing and the machine keeps rebooting.',
            'I need help with a failed NIC card on the corporate desktop.',
            'The virtualization host is down after a BIOS security policy change.',
            'I have a blue screen error on my desktop and suspect faulty RAM.',
            'The printer hardware is not responding and shows a device failure code.',
            'The USB-C docking station is not powering the external monitors.',
            'Our edge router hardware has failed and needs a replacement module.',
            'The desktop audio device is missing from device manager after reboot.',
            'A server chassis fan has failed and is causing overheating alerts.',
            'The laptop keyboard is broken and needs a hardware service ticket.',
            'The network switch module has a hardware fault LED for port 3.',
            'There is an error on the compute blade after a hardware firmware upgrade.',
        ],
        'Application': [
            'The web application returns a 500 error when submitting the order form.',
            'Excel crashes when opening the macro-enabled workbook with a plugin error.',
            'The reporting dashboard times out when loading quarterly sales data.',
            'An internal app throws a runtime exception when saving the record.',
            'Our SaaS portal is failing with a stack trace after the last release.',
            'The client software cannot connect to the database due to an API error.',
            'The mobile app is stuck on the login screen after the new patch.',
            'The CRM software displays corrupted fields after the update.',
            'A browser extension conflict is causing our web app to freeze.',
            'The desktop application fails to start with an unhandled exception.',
            'The newly deployed app version crashes on the checkout page.',
            'Reports are not generating in the analytics application after login.',
            'I get a 404 error on the internal knowledge base application.',
            'The application cannot upload files and shows an unknown error.',
            'Our collaboration tool hangs when sharing documents with the team.',
        ],
        'Database': [
            'The PostgreSQL database is timing out when querying the orders table.',
            'A deadlock occurred in the DB cluster during the batch job.',
            'The Oracle database replication lag is causing stale reads.',
            'The SQL Server instance is throwing connection pool exhausted errors.',
            'The database backup restore failed with checksum mismatch.',
            'The query optimizer is causing slow joins on the customer dataset.',
            'The data warehouse load task is failing with a database error.',
            'The DB schema migration failed during the deployment window.',
            'The database CPU usage is at 100% and transactions are delaying.',
            'A table is locked and the reporting query cannot complete.',
            'The database user does not have access to the inventory schema.',
            'The DB connection string is invalid in the application configuration.',
            'There are missing indexes causing slow database queries.',
            'The database restore process cannot find the backup media.',
            'The replication service reports a failed log shipping task.',
        ],
        'Storage': [
            'The SAN volume is full and backup jobs are failing.',
            'I cannot access the shared network drive storage folder.',
            'The storage array reports degraded performance on the NAS share.',
            'A file restore request failed from the backup storage appliance.',
            'The cloud storage bucket is not syncing with our local archive.',
            'The archive vault search returns no results for saved documents.',
            'The shared storage capacity warning keeps appearing on my desktop.',
            'The backup snapshot failed due to insufficient storage space.',
            'The file server storage pool is offline after the maintenance reboot.',
            'We need a new storage allocation for the project repository.',
            'The archive server cannot mount the storage volume.',
            'The object storage service is returning permission denied errors.',
            'The storage cluster lost quorum and cannot serve files.',
            'The remote storage array is reporting SMART disk failures.',
            'The storage replication service is showing latency spikes.',
        ],
        'Network': [
            'I cannot connect to the corporate Wi-Fi after the router firmware update.',
            'There is packet loss on the VPN tunnel to the remote office.',
            'Our site-to-site network link is down and critical services are offline.',
            'The network switch port is flapping and causing intermittent outages.',
            'The DNS server is failing to resolve internal hostnames.',
            'The firewall is blocking traffic to the service endpoint unexpectedly.',
            'The MPLS connection has high latency and dropped packets.',
            'The router configuration change broke connectivity for several users.',
            'The wireless access point is not broadcasting the corporate SSID.',
            'Network throughput is very slow for the storage replication job.',
            'The VPN gateway authentication is timing out for remote users.',
            'We are seeing repeated BGP route withdrawals from the ISP.',
            'The VOIP phones are losing calls because of network jitter.',
            'The network monitoring shows a storm on the distribution switch.',
            'The service desk cannot reach the application due to subnet misconfiguration.',
        ],
    }
    samples = []
    for category, texts in templates.items():
        dept = cat_to_dept[category]
        for text in texts:
            samples.append({'text': text, 'expected_department': dept})
    samples = samples[:100]

    ticket_service = TicketService(session)
    results = []
    for idx, sample in enumerate(samples, start=1):
        ticket = Ticket(
            ticket_id=f'SYN-{idx:03d}',
            user_id=user.user_id,
            title=f'Synthetic issue {idx}',
            description_raw=sample['text'],
            description_sanitized=sample['text'],
            urgency='medium',
            status='RECEIVED',
            hand='1',
            confidence=0.0,
            department_queue='General',
            priority='P1',
            sla_hours=24,
            escalation_required=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(ticket)
        session.commit()
        start = time.perf_counter()
        result = ticket_service.process_ticket(ticket)
        elapsed = time.perf_counter() - start
        results.append({
            'expected': sample['expected_department'],
            'predicted': result.routing.department_queue if result.routing else 'General',
            'elapsed': elapsed,
            'hand': result.decision.hand,
            'status': result.decision.status,
        })

    correct = sum(1 for r in results if r['predicted'] == r['expected'])
    accuracy = correct / len(results)
    dept_labels = sorted(set(r['expected'] for r in results))
    counts = {label: 0 for label in dept_labels}
    pred_counts = {}
    tp = {label: 0 for label in dept_labels}
    for r in results:
        counts[r['expected']] += 1
        pred_counts[r['predicted']] = pred_counts.get(r['predicted'], 0) + 1
        if r['predicted'] == r['expected']:
            tp[r['expected']] += 1
    precision = {}
    recall = {}
    f1 = {}
    for label in dept_labels:
        tpv = tp[label]
        fp = pred_counts.get(label, 0) - tpv
        fn = counts[label] - tpv
        precision[label] = tpv / (tpv + fp) if tpv + fp else 0.0
        recall[label] = tpv / (tpv + fn) if tpv + fn else 0.0
        f1[label] = 2 * precision[label] * recall[label] / (precision[label] + recall[label]) if precision[label] + recall[label] else 0.0
    macro_f1 = sum(f1.values()) / len(f1)
    micro_tp = sum(tp.values())
    micro_fp = sum(pred_counts.get(l, 0) - tp[l] for l in dept_labels)
    micro_fn = sum(counts[l] - tp[l] for l in dept_labels)
    micro_precision = micro_tp / (micro_tp + micro_fp) if micro_tp + micro_fp else 0.0
    micro_recall = micro_tp / (micro_tp + micro_fn) if micro_tp + micro_fn else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if micro_precision + micro_recall else 0.0
    deflection_rate = sum(1 for r in results if r['hand'] == '1') / len(results)
    latencies = [r['elapsed'] for r in results]
    avg_latency = sum(latencies) / len(latencies)
    median_latency = sorted(latencies)[len(latencies)//2]
    print('TOTAL_TICKETS', len(results))
    print('CORRECT', correct)
    print('ACCURACY', f'{accuracy:.4f}')
    print('MICRO_F1', f'{micro_f1:.4f}')
    print('MACRO_F1', f'{macro_f1:.4f}')
    print('DEFLECTION_RATE', f'{deflection_rate:.4f}')
    print('AVG_LATENCY_SEC', f'{avg_latency:.4f}')
    print('MEDIAN_LATENCY_SEC', f'{median_latency:.4f}')
    print('MAX_LATENCY_SEC', f'{max(latencies):.4f}')
    print('MIN_LATENCY_SEC', f'{min(latencies):.4f}')
    print('PER_TICKET_COST_INR', '0.000')
    print('PER_TICKET_COST_USD', '0.000')
    for label in dept_labels:
        print('LABEL', label, 'COUNT', counts[label], 'PREC', f'{precision[label]:.4f}', 'REC', f'{recall[label]:.4f}', 'F1', f'{f1[label]:.4f}')

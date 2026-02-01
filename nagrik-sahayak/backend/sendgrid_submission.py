import os
import uuid
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def submit_via_email(report):
    if not SENDGRID_API_KEY:
        return {"status": "error", "message": "SendGrid API key not set"}

    reference_id = "NS-" + uuid.uuid4().hex[:8].upper()

    message = Mail(
        from_email="afikureshi7@gmail.com",
        to_emails="afikureshi7@gmail.com",  # test
        subject=f"Civic Issue Report ({reference_id})",
        html_content=f"""
        <h2>Civic Issue Report</h2>

        <p><b>Reference ID:</b> {reference_id}</p>
        <p><b>City:</b> {report['city']}</p>
        <p><b>Urgency:</b> {report['urgency']}</p>

        <hr/>

        <pre style="white-space: pre-wrap; font-family: Arial;">
{report['description']}
        </pre>

        <p><i>Reported on: {datetime.now()}</i></p>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        return {
            "status": "success",
            "reference_id": reference_id,
            "sendgrid_status": response.status_code
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

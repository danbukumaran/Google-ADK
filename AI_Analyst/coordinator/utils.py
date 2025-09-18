
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
import time
import smtplib
from email.mime.text import MIMEText

# update state in the session
def update_state(state_changes: dict, invocation_id: str, author_name: str):

    # --- Define State Changes ---
    current_time = time.time()
  
    # --- Create Event with Actions ---
    actions_with_update = EventActions(state_delta=state_changes)

    system_event = Event(
        invocation_id= invocation_id,
        author=author_name,
        actions=actions_with_update,
        timestamp=current_time
    )

    return system_event



def send_email(to_email: str, subject: str, body: str):
    # Email configuration
    sender_email = "your_email@example.com"  
    password = "your_password"              
                                           
    # SMTP server details (for Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email

    try:
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(sender_email, password) # Authenticate with your credentials
            server.send_message(message) # Send the email

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
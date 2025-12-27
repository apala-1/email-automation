import csv
import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Loading environment variables from .env
load_dotenv()

# Logging setup
os.makedirs("src/logs", exist_ok=True)
logging.basicConfig(
    filename="src/logs/email.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def load_smtp_config():
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "user": os.getenv("SMTP_USER"),
        "pass": os.getenv("SMTP_PASS")
    }

def render_template(path: str, context: dict) -> str:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for k, v in context.items():
        content = content.replace(f"{{{{{k}}}}}", str(v))
    return content

def send_email(smtp_cfg, to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = smtp_cfg["user"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_cfg["host"], smtp_cfg["port"], context=context) as server:
            server.login(smtp_cfg["user"], smtp_cfg["pass"])
            server.sendmail(smtp_cfg["user"], to_email, msg.as_string())
        logging.info(f"EMAIL_SENT to={to_email} subject={subject}")
        return True
    except Exception as e:
        logging.error(f"EMAIL_FAILED to={to_email} subject={subject} error={e}")
        return False

def main():
    smtp_cfg = load_smtp_config()
    if not smtp_cfg["user"] or not smtp_cfg["pass"]:
        raise RuntimeError("Missing SMTP_USER/SMTP_PASS in .env")

    with open("emails/contacts.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            context = {"name": row["name"]}
            subject = render_template("emails/templates/subject.txt", context)
            body = render_template("emails/templates/body.txt", context)
            ok = send_email(smtp_cfg, row["email"], subject, body)
            print(("Sent" if ok else "Failed"), "->", row["email"])

if __name__ == "__main__":
    main()

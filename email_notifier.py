from logging_config import logger
import smtplib
from email.mime.text import MIMEText

from configuration import Configuration

class EmailNotifier:
    def __init__(self, config: Configuration):
        self.smtp_server = config.get('email','host')
        self.smtp_port = int(config.get('email','port', fallback=25))
        self.username = config.get('email','username')
        self.password = config.get('email','password')
        self.from_addr = config.get('email','from_addr')
        self.to_addr = config.get('email', 'to_addr')

    def send_email(self, subject, message):
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.sendmail(self.from_addr, [self.to_addr], msg.as_string())
            logger.debug("E-Mail wurde gesendet.")
        except Exception as e:
            logger.error(f"Fehler beim Senden der E-Mail: {e}")
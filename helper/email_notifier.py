import ssl

from helper.configuration import Configuration
from logging_config import logger
import smtplib
from email.mime.text import MIMEText



class EmailNotifier:
    def __init__(self, config: Configuration):
        self.smtp_server = config.get('smtp','host')
        self.smtp_port = int(config.get('smtp','port', fallback=25))
        self.username = config.get('smtp','username')
        self.password = config.get('smtp','password')
        self.from_addr = config.get('smtp','from_addr')
        self.to_addr = config.get('smtp', 'to_addr')

    def send_email(self, subject, message):
        msg = MIMEText(message)
        msg["Subject"] = "Hetzner Control - " + subject
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.connect()
                server.login(self.username, self.password)
                server.sendmail(self.from_addr, [self.to_addr], msg.as_string())
            logger.debug("E-Mail was send.")
        except Exception as e:
            logger.error(f"Error on sending e-mail:")
            logger.exception(e)
import pytest
import smtplib
from unittest.mock import patch, MagicMock
from email.mime.text import MIMEText

from email_notifier import EmailNotifier
from configuration import Configuration

@pytest.fixture
def mock_config():
    """Mock Configuration object with sample SMTP details."""
    config = MagicMock(spec=Configuration)
    config.get.side_effect = lambda section, key, fallback=None: {
        ("smtp", "host"): "smtp.example.com",
        ("smtp", "port"): "465",
        ("smtp", "username"): "user@example.com",
        ("smtp", "password"): "securepassword",
        ("smtp", "from_addr"): "from@example.com",
        ("smtp", "to_addr"): "to@example.com",
    }.get((section, key), fallback)
    return config

@pytest.fixture
def email_notifier(mock_config):
    """Initialize EmailNotifier with mocked config."""
    return EmailNotifier(mock_config)

@patch("smtplib.SMTP_SSL")
def test_send_email_success(mock_smtp, email_notifier):
    """Test successful email sending."""
    mock_server = mock_smtp.return_value  # Mock the SMTP server
    email_notifier.send_email("Test Subject", "Test Message")

    # Ensure SMTP_SSL was called with correct parameters
    mock_smtp.assert_called_once_with("smtp.example.com", 465)

    # Ensure SMTP server commands were called
    mock_server.__enter__.return_value.login.assert_called_once_with("user@example.com", "securepassword")
    mock_server.__enter__.return_value.sendmail.assert_called_once_with(
        "from@example.com", ["to@example.com"], MIMEText("Test Message").as_string()
    )

@patch("smtplib.SMTP_SSL", side_effect=smtplib.SMTPException("SMTP connection failed"))
def test_send_email_failure(mock_smtp, email_notifier, caplog):
    """Test email sending failure and error logging."""
    with pytest.raises(smtplib.SMTPException, match="SMTP connection failed"):
        email_notifier.send_email("Test Subject", "Test Message")

    # Verify log output contains an error message
    assert "Error on sending e-mail" in caplog.text

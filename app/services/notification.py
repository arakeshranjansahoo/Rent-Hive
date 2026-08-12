"""
RentHive Notification Services
Version: 6.0 - SMTP Email Only (No SMS)
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Email notification service via SMTP"""

    @staticmethod
    def _get_mail_config():
        """Get mail configuration from app config"""
        return {
            'mail_server': current_app.config.get('MAIL_SERVER', 'smtp.gmail.com'),
            'mail_port': current_app.config.get('MAIL_PORT', 587),
            'mail_use_tls': current_app.config.get('MAIL_USE_TLS', True),
            'mail_username': current_app.config.get('MAIL_USERNAME'),
            'mail_password': current_app.config.get('MAIL_PASSWORD')
        }

    @staticmethod
    def send_email(to_email, subject, body, html_body=None):
        """
        Send email notification via SMTP

        Args:
            to_email: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)

        Returns:
            dict: {'success': bool, 'message': str}
        """
        config = EmailService._get_mail_config()

        if not config['mail_username'] or not config['mail_password']:
            logger.warning(f"Email not configured. Would send to {to_email}: {subject}")
            return {
                'success': True,
                'message': 'Email skipped (not configured)',
                'sent_at': datetime.now().isoformat()
            }

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = config['mail_username']
            msg['To'] = to_email

            msg.attach(MIMEText(body, 'plain'))

            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(config['mail_server'], config['mail_port']) as server:
                if config['mail_use_tls']:
                    server.starttls()
                server.login(config['mail_username'], config['mail_password'])
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return {
                'success': True,
                'message': 'Email sent successfully',
                'sent_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}',
                'sent_at': datetime.now().isoformat()
            }

    @staticmethod
    def send_bill_notification(bill):
        """Send bill generation notification"""
        tenant_email = bill.tenant.user.email
        subject = f"New Bill Generated - {bill.bill_number}"

        body = f"""
Dear {bill.tenant.user.full_name},

A new bill has been generated for your room.

Bill Number: {bill.bill_number}
Bill Month: {bill.bill_month}
Total Amount: Rs.{bill.total_amount:.2f}
Due Date: {bill.due_date.strftime('%d-%m-%Y')}

Please log in to your account to view and pay the bill.

Regards,
RentHive Team
"""

        return EmailService.send_email(tenant_email, subject, body)

    @staticmethod
    def send_payment_confirmation(bill):
        """Send payment confirmation"""
        tenant_email = bill.tenant.user.email
        subject = f"Payment Received - {bill.bill_number}"

        body = f"""
Dear {bill.tenant.user.full_name},

We have received your payment for bill {bill.bill_number}.

Amount Paid: Rs.{bill.amount_paid:.2f}
Payment Date: {bill.payment_date.strftime('%d-%m-%Y')}
Payment Method: {bill.payment_method}
Balance: Rs.{bill.balance:.2f}

Thank you for your payment!

Regards,
RentHive Team
"""

        return EmailService.send_email(tenant_email, subject, body)

    @staticmethod
    def send_welcome_email(user, temporary_password=None):
        """Send welcome email to new user"""
        subject = "Welcome to RentHive!"

        body = f"""
Dear {user.full_name},

Welcome to RentHive! Your account has been created successfully.

Username: {user.username}
Email: {user.email}
"""

        if temporary_password:
            body += f"\nTemporary Password: {temporary_password}\n\nPlease change your password after first login."

        body += """

You can now log in to manage your rental activities.

Regards,
RentHive Team
"""

        return EmailService.send_email(user.email, subject, body)

    @staticmethod
    def send_overdue_reminder(bill):
        """Send overdue payment reminder"""
        tenant_email = bill.tenant.user.email
        subject = f"Payment Reminder - Bill {bill.bill_number} is Overdue"

        body = f"""
Dear {bill.tenant.user.full_name},

This is a reminder that your bill payment is overdue.

Bill Number: {bill.bill_number}
Bill Month: {bill.bill_month}
Total Amount: Rs.{bill.total_amount:.2f}
Amount Paid: Rs.{bill.amount_paid:.2f}
Balance: Rs.{bill.balance:.2f}
Due Date: {bill.due_date.strftime('%d-%m-%Y')} (OVERDUE)

Please make the payment at the earliest to avoid late fees.

Regards,
RentHive Team
"""

        return EmailService.send_email(tenant_email, subject, body)


class NotificationManager:
    """Centralized notification manager - Email only"""

    @staticmethod
    def notify_new_bill(bill):
        """
        Send notifications for new bill (email only)

        Args:
            bill: Bill object
        """
        return {'email': EmailService.send_bill_notification(bill)}

    @staticmethod
    def notify_payment_received(bill):
        """Send payment confirmation notifications (email only)"""
        return {'email': EmailService.send_payment_confirmation(bill)}

    @staticmethod
    def notify_overdue_bills(bills):
        """Send reminders for overdue bills (email only)"""
        results = []

        for bill in bills:
            result = {
                'bill_id': bill.id,
                'bill_number': bill.bill_number,
                'email': EmailService.send_overdue_reminder(bill)
            }
            results.append(result)

        return results

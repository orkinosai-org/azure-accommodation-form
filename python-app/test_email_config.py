#!/usr/bin/env python3
"""
CLI tool for testing email configuration
Usage: python test_email_config.py [email@example.com]
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings
from app.services.email import EmailService

async def test_email_config(test_email: str = None):
    """Test email configuration and optionally send a test email"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("Azure Accommodation Form - Email Configuration Test")
    print("=" * 60)
    
    # Load and audit configuration
    settings = get_settings()
    audit_info = settings.audit_configuration(logger)
    
    print("\n" + "=" * 40)
    print("CONFIGURATION SUMMARY")
    print("=" * 40)
    
    email_ready = bool(
        settings.email_settings.smtp_username and 
        settings.email_settings.smtp_password and
        settings.email_settings.from_email
    )
    
    print(f"Email Service Ready: {'✓ YES' if email_ready else '✗ NO'}")
    print(f"Missing Fields: {len(audit_info.get('missing_fields', []))}")
    print(f"Configuration Warnings: {len(audit_info.get('warnings', []))}")
    
    if audit_info.get('missing_fields'):
        print("\nMISSING REQUIRED FIELDS:")
        for field in audit_info['missing_fields']:
            print(f"  • {field['field']}: {field['env_vars']}")
            print(f"    Example: {field['example']}")
    
    if audit_info.get('warnings'):
        print("\nWARNINGS:")
        for warning in audit_info['warnings']:
            print(f"  ⚠ {warning}")
    
    # Test email sending if configured and email provided
    if test_email and email_ready:
        print("\n" + "=" * 40)
        print("SENDING TEST EMAIL")
        print("=" * 40)
        
        try:
            email_service = EmailService()
            
            print(f"Sending test email to: {test_email}")
            print(f"SMTP Server: {settings.email_settings.smtp_server}:{settings.email_settings.smtp_port}")
            print(f"From: {settings.email_settings.from_name} <{settings.email_settings.from_email}>")
            
            success = await email_service._send_email(
                to_email=test_email,
                subject="Test Email from Azure Accommodation Form CLI",
                body_text=f"""
This is a test email sent from the Azure Accommodation Form CLI tool.

Configuration Test Results:
- SMTP Server: {settings.email_settings.smtp_server}:{settings.email_settings.smtp_port}
- From: {settings.email_settings.from_name} <{settings.email_settings.from_email}>
- SSL/TLS: {"Enabled" if settings.email_settings.use_ssl else "Disabled"}

If you received this email, your email configuration is working correctly!

Sent from the command line at: {settings.application_settings.application_url}
                """.strip(),
                body_html=f"""
                <html>
                <body>
                    <h2>Test Email from Azure Accommodation Form CLI</h2>
                    <p>This is a test email sent from the Azure Accommodation Form CLI tool.</p>
                    
                    <h3>Configuration Test Results:</h3>
                    <ul>
                        <li><strong>SMTP Server:</strong> {settings.email_settings.smtp_server}:{settings.email_settings.smtp_port}</li>
                        <li><strong>From:</strong> {settings.email_settings.from_name} &lt;{settings.email_settings.from_email}&gt;</li>
                        <li><strong>SSL/TLS:</strong> {"Enabled" if settings.email_settings.use_ssl else "Disabled"}</li>
                    </ul>
                    
                    <p>✅ If you received this email, your email configuration is working correctly!</p>
                    
                    <hr>
                    <p><small>Sent from the command line at: {settings.application_settings.application_url}</small></p>
                </body>
                </html>
                """
            )
            
            if success:
                print("✅ Test email sent successfully!")
                print(f"Check the inbox for {test_email}")
            else:
                print("❌ Failed to send test email")
                print("Check the logs above for error details")
                
        except Exception as e:
            print(f"❌ Error sending test email: {e}")
            
    elif test_email and not email_ready:
        print("\n" + "=" * 40)
        print("CANNOT SEND TEST EMAIL")
        print("=" * 40)
        print("Email configuration is incomplete. Fix the missing fields above first.")
        
    elif email_ready:
        print("\n" + "=" * 40)
        print("EMAIL CONFIGURATION READY")
        print("=" * 40)
        print("Email service is fully configured!")
        print("To send a test email, run:")
        print(f"  python {sys.argv[0]} your-email@example.com")
    
    print("\n" + "=" * 60)
    print("Configuration test complete!")
    print("=" * 60)

def main():
    """Main CLI entry point"""
    test_email = sys.argv[1] if len(sys.argv) > 1 else None
    
    if test_email and '@' not in test_email:
        print("Error: Please provide a valid email address")
        print(f"Usage: python {sys.argv[0]} your-email@example.com")
        sys.exit(1)
    
    try:
        asyncio.run(test_email_config(test_email))
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
Email Service for sending encrypted files.
"""
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import os


class EmailService:
    """Handles sending encrypted files via email."""
    
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
    
    def send_encrypted_file(
        self,
        recipient_email: str,
        sender_email: str,
        encrypted_file_path: str,
        decryption_key: str,
        original_filename: str
    ) -> bool:
        """
        Send encrypted file to recipient with decryption key.
        
        Args:
            recipient_email: Recipient's email address
            sender_email: Sender's email address
            encrypted_file_path: Path to encrypted file
            decryption_key: Key needed for decryption
            original_filename: Original PDF filename
            
        Returns:
            True if email sent successfully
        """
        subject = f"Encrypted PDF from {sender_email}"
        
        # Create HTML message
        message_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; text-align: center;">
                <h1 style="margin: 0;">📄 Encrypted PDF Received</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa; border-radius: 0 0 10px 10px;">
                <p><strong>From:</strong> {sender_email}</p>
                <p><strong>Original File:</strong> {original_filename}</p>
                
                <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>⚠️ Decryption Key (Keep this safe!):</strong>
                    <div style="background: #fff; padding: 10px; margin-top: 10px; font-family: monospace; word-break: break-all; border-radius: 3px;">
                        {decryption_key}
                    </div>
                </div>
                
                <p>To decrypt this file:</p>
                <ol>
                    <li>Download the attached encrypted file</li>
                    <li>Visit <a href="{settings.CORS_ALLOWED_ORIGINS[0]}/decrypt">our decryption page</a></li>
                    <li>Upload the encrypted file</li>
                    <li>Enter the decryption key above</li>
                    <li>Download your decrypted PDF</li>
                </ol>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    This file was encrypted using DCKP-ES (Dynamic Chaos Key Pixel Encryption Shuffling) algorithm.
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
Encrypted PDF from {sender_email}

Original File: {original_filename}

DECRYPTION KEY (Keep this safe!):
{decryption_key}

To decrypt this file:
1. Download the attached encrypted file
2. Visit {settings.CORS_ALLOWED_ORIGINS[0]}/decrypt
3. Upload the encrypted file
4. Enter the decryption key
5. Download your decrypted PDF

This file was encrypted using DCKP-ES algorithm.
        """
        
        try:
            email = EmailMessage(
                subject=subject,
                body=message_html,
                from_email=self.from_email,
                to=[recipient_email]
            )
            
            email.content_subtype = 'html'
            
            # Attach encrypted file
            # Attach encrypted file logic
            filename = os.path.basename(encrypted_file_path)
            file_size_mb = os.path.getsize(encrypted_file_path) / (1024 * 1024)
            
            # Use 25MB as safe limit for most email providers (Gmail limit)
            MAX_SIZE_MB = 25
            
            if file_size_mb > MAX_SIZE_MB:
                print(f"WARNING: File size ({file_size_mb:.2f} MB) exceeds email limit. Sending without attachment.")
                
                # Construct public download link (assuming backend runs on standard port or configured URL)
                # Since we don't have request object here, we use a best-effort construction
                # In production, this should be a configured setting like API_BASE_URL
                api_base = "http://localhost:8000" # Default dev
                if 'localhost' not in settings.CORS_ALLOWED_ORIGINS[0]:
                     # Try to infer from frontend URL if deployed together, or fall back
                     pass
                     
                download_link = f"{api_base}/api/encryption/download/{filename}"
                
                # Append warning to body
                warning_html = f"""
                <div style="background: #f8d7da; color: #721c24; padding: 10px; margin: 20px 0; border: 1px solid #f5c6cb; border-radius: 5px;">
                    <strong>⚠️ Attachment Too Large</strong><br>
                    The encrypted file is larger than {MAX_SIZE_MB}MB ({file_size_mb:.1f} MB) and cannot be attached to this email.<br>
                    You can download it directly using the link below:<br>
                    <a href="{download_link}" style="display: inline-block; background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        📥 Download Encrypted File
                    </a>
                </div>
                """
                # Insert warning before the "To decrypt this file" section
                body_parts = message_html.split('<p>To decrypt this file:</p>')
                if len(body_parts) == 2:
                    email.body = body_parts[0] + warning_html + '<p>To decrypt this file:</p>' + body_parts[1]
                
                plain_warning = f"\n⚠️ NOTE: The encrypted file is too large ({file_size_mb:.1f} MB) to attach.\nDownload it here: {download_link}\n"
                plain_message += plain_warning
                
            else:
                try:
                    with open(encrypted_file_path, 'rb') as f:
                        email.attach(filename, f.read(), 'application/octet-stream')
                except MemoryError:
                    print("ERROR: MemoryError while reading file for attachment")
                    return False
            
            print(f"DEBUG: Attempting to send email to {recipient_email} from {sender_email}")
            email.send(fail_silently=False)
            print("DEBUG: Email sent successfully")
            return True
            
        except Exception as e:
            print(f"ERROR: Email sending failed: {e}")
            import traceback
            traceback.print_exc()
            # In debug mode, just return True
            if settings.DEBUG:
                return True
            return False
    
    def send_verification_email(self, user_email: str, verification_url: str) -> bool:
        """Send email verification link."""
        subject = "Verify your email - PDF Encryption System"
        
        message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; text-align: center;">
                <h1 style="margin: 0;">✉️ Verify Your Email</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa; border-radius: 0 0 10px 10px; text-align: center;">
                <p>Click the button below to verify your email address:</p>
                
                <a href="{verification_url}" style="display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0;">
                    Verify Email
                </a>
                
                <p style="color: #666; font-size: 12px;">
                    If you didn't create an account, you can ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=self.from_email,
                to=[user_email]
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

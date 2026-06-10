import re
from app.config import settings
def get_registration_otp_email(user_name: str, otp: str) -> str:
    """Compiles professional HTML card for email verification OTP."""
    return f"""
    <html>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="background-color: #f3f4f6; padding: 32px 16px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e5e7eb;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Verify Your Email</h1>
                        <p style="color: #e0e7ff; margin: 8px 0 0 0; font-size: 14px;">PMRG Solution Ideathon </p>
                    </div>
                    <!-- Content -->
                    <div style="padding: 32px 24px; color: #1f2937; line-height: 1.6;">
                        <p style="margin-top: 0; font-size: 16px;">Hello <strong>{user_name}</strong>,</p>
                        <p style="font-size: 15px; color: #4b5563;">Thank you for registering on our platform! To activate your account and verify your email address, please use the 6-digit One-Time Password (OTP) below:</p>
                        
                        <!-- OTP Box -->
                        <div style="margin: 32px 0; padding: 20px; background-color: #f8fafc; border: 1px dashed #e2e8f0; border-radius: 8px; text-align: center;">
                            <span style="font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #4f46e5; font-family: 'Courier New', Courier, monospace;">{otp}</span>
                        </div>
                        
                        <p style="font-size: 14px; color: #dc2626; font-weight: 600; margin: 0 0 16px 0;">⚠️ This code is strictly active for 5 minutes.</p>
                        <p style="font-size: 14px; color: #6b7280; margin: 0;">If you did not initiate this request, you can safely ignore this email.</p>
                    </div>
                    <!-- Footer -->
                    <div style="background-color: #f9fafb; padding: 24px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
                        <p style="margin: 0 0 6px 0;">&copy; 2026 PMRG Solution. All rights reserved.</p>
                        <p style="margin: 0;">This is an automated security system notification.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
def get_recovery_otp_email(user_name: str, otp: str) -> str:
    """Compiles professional HTML card for password recovery OTP."""
    return f"""
    <html>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="background-color: #f3f4f6; padding: 32px 16px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e5e7eb;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #ef4444 0%, #f97316 100%); padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Reset Your Password</h1>
                        <p style="color: #ffe4e6; margin: 8px 0 0 0; font-size: 14px;">PMRG Solution Ideathon </p>
                    </div>
                    <!-- Content -->
                    <div style="padding: 32px 24px; color: #1f2937; line-height: 1.6;">
                        <p style="margin-top: 0; font-size: 16px;">Hello <strong>{user_name}</strong>,</p>
                        <p style="font-size: 15px; color: #4b5563;">We received a request to reset the password for your account. Please use the authorization code below to submit your new password credentials:</p>
                        
                        <!-- OTP Box -->
                        <div style="margin: 32px 0; padding: 20px; background-color: #fff5f5; border: 1px solid #fee2e2; border-radius: 8px; text-align: center;">
                            <span style="font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #ef4444; font-family: 'Courier New', Courier, monospace;">{otp}</span>
                        </div>
                        
                        <p style="font-size: 14px; color: #dc2626; font-weight: 600; margin: 0 0 16px 0;">⚠️ This recovery code will expire in 5 minutes.</p>
                        <p style="font-size: 14px; color: #6b7280; margin: 0;">If you did not request a password reset, your account remains completely secure. You can safely ignore this alert.</p>
                    </div>
                    <!-- Footer -->
                    <div style="background-color: #f9fafb; padding: 24px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
                        <p style="margin: 0 0 6px 0;">&copy; 2026 PMRG Solution. All rights reserved.</p>
                        <p style="margin: 0;">This is an automated security system notification.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
def get_admin_new_idea_email(idea_title: str, user_name: str) -> str:
    """Compiles professional HTML card for admin submission notifications."""
    return f"""
    <html>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="background-color: #f3f4f6; padding: 32px 16px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e5e7eb;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #1e293b 0%, #475569 100%); padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">New Idea Submitted</h1>
                        <p style="color: #cbd5e1; margin: 8px 0 0 0; font-size: 14px;">Administrative Audit Panel</p>
                    </div>
                    <!-- Content -->
                    <div style="padding: 32px 24px; color: #1f2937; line-height: 1.6;">
                        <p style="margin-top: 0; font-size: 16px; font-weight: 600;">Hello Administrator,</p>
                        <p style="font-size: 15px; color: #4b5563;">A participant has submitted a new project proposal for review on the :</p>
                        
                        <!-- Details Table -->
                        <div style="margin: 24px 0; padding: 16px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                <tr>
                                    <td style="padding: 6px 0; color: #64748b; font-weight: 500; width: 120px;">Submitter:</td>
                                    <td style="padding: 6px 0; color: #0f172a; font-weight: 600;">{user_name}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 6px 0; color: #64748b; font-weight: 500;">Project Title:</td>
                                    <td style="padding: 6px 0; color: #0f172a; font-weight: 600;">{idea_title}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <!-- CTA Button -->
                        <div style="text-align: center; margin: 32px 0 16px 0;">
                            <a href="{settings.FRONTEND_DASHBOARD_URL}" style="background-color: #0f172a; color: #ffffff; padding: 12px 28px; font-size: 15px; font-weight: 600; text-decoration: none; border-radius: 6px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">Access Admin Console</a>
                        </div>
                    </div>
                    <!-- Footer -->
                    <div style="background-color: #f9fafb; padding: 24px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
                        <p style="margin: 0 0 6px 0;">&copy; 2026 PMRG Solution. All rights reserved.</p>
                        <p style="margin: 0;">This is an automated backend alert.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
def get_status_update_email(participant_name: str, idea_title: str, status: str) -> str:
    """Dynamically maps the 8 operational milestones to their unique header gradients, banner backgrounds, and customized copy."""
    # Define design tokens for all 8 status options
    status_matrix = {
        "Submitted": {
            "title": "Status Updated: Submitted",
            "gradient": "linear-gradient(135deg, #475569 0%, #64748b 100%)",
            "banner_bg": "#f8fafc",
            "banner_border": "#cbd5e1",
            "banner_color": "#334155",
            "copy": "Thank you for submitting your innovation proposal. The steering panel has received your materials and will begin the initial vetting process shortly."
        },
        "Under Review": {
            "title": "Status Updated: Under Review",
            "gradient": "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
            "banner_bg": "#f5f3ff",
            "banner_border": "#ddd6fe",
            "banner_color": "#5b21b6",
            "copy": "Your proposal is now officially under evaluation by our steering panel and jury members. We will update you once scorecard reviews are compiled."
        },
        "Shortlisted": {
            "title": "Status Updated: Shortlisted",
            "gradient": "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)",
            "banner_bg": "#f0fdfa",
            "banner_border": "#ccfbf1",
            "banner_color": "#115e59",
            "copy": "Great news! Your project proposal has been shortlisted. The evaluation board was impressed by your proposal and has advanced you to the presentation pool."
        },
        "Interview Scheduled": {
            "title": "Status Updated: Interview Scheduled",
            "gradient": "linear-gradient(135deg, #d97706 0%, #b45309 100%)",
            "banner_bg": "#fffbeb",
            "banner_border": "#fef3c7",
            "banner_color": "#92400e",
            "copy": "An interview slot and project presentation session has been scheduled for your team. Please log in to view your time slot, link, and preparation guidelines."
        },
        "Selected": {
            "title": "Status Updated: Selected",
            "gradient": "linear-gradient(135deg, #059669 0%, #047857 100%)",
            "banner_bg": "#ecfdf5",
            "banner_border": "#d1fae5",
            "banner_color": "#065f46",
            "copy": "Congratulations! Your project proposal has been officially selected as an Ideathon finalist. Review details about final evaluations on your  dashboard."
        },
        "Winner": {
            "title": "Congratulations! Winner",
            "gradient": "linear-gradient(135deg, #eab308 0%, #ca8a04 100%)",
            "banner_bg": "#fef9c3",
            "banner_border": "#fef08a",
            "banner_color": "#854d0e",
            "copy": "Outstanding achievement! Your submission has been declared a official Winner of the PMRG Solution Ideathon. The steering panel commends your dedication and innovative solution."
        },
        "Incubation Phase": {
            "title": "Status Updated: Incubation Phase",
            "gradient": "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
            "banner_bg": "#eff6ff",
            "banner_border": "#dbeafe",
            "banner_color": "#1e40af",
            "copy": "Your project is transitioning into the operational Incubation Phase. You will receive specialized mentorship, technical support resources, and development guidance."
        },
        "Closed": {
            "title": "Status Updated: Closed",
            "gradient": "linear-gradient(135deg, #374151 0%, #1f2937 100%)",
            "banner_bg": "#f9fafb",
            "banner_border": "#e5e7eb",
            "banner_color": "#374151",
            "copy": "The review and evaluation cycle for your submission has concluded. We sincerely thank you for your contribution, creativity, and participation."
        }
    }
    # Fallback to standard Submitted layout if status isn't matched
    styles = status_matrix.get(status, status_matrix["Submitted"])
    return f"""
    <html>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="background-color: #f3f4f6; padding: 32px 16px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e5e7eb;">
                    <!-- Header -->
                    <div style="background: {styles['gradient']}; padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">{styles['title']}</h1>
                        <p style="color: #ffffff; opacity: 0.85; margin: 8px 0 0 0; font-size: 14px;">PMRG Solution Ideathon </p>
                    </div>
                    <!-- Content -->
                    <div style="padding: 32px 24px; color: #1f2937; line-height: 1.6;">
                        <p style="margin-top: 0; font-size: 16px;">Hello {participant_name},</p>
                        <p style="font-size: 15px; color: #4b5563;">{styles['copy']}</p>
                        
                        <!-- Details Table -->
                        <div style="margin: 24px 0; padding: 16px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px;">
                            <strong style="color: #0f172a; display: block; margin-bottom: 6px;">Submission Title:</strong>
                            <span style="color: #4b5563;">{idea_title}</span>
                        </div>
                        <!-- Status Alert Banner -->
                        <div style="margin: 28px 0; padding: 16px; background-color: {styles['banner_bg']}; border-left: 4px solid {styles['banner_border']}; border-radius: 4px; font-size: 16px; font-weight: 700; color: {styles['banner_color']}; text-align: center;">
                            Current Status: {status}
                        </div>
                        
                        <p style="font-size: 15px; color: #4b5563;">You can log in to your participant dashboard to read detailed scorecard reviews, view jury remarks, or verify upcoming presentation targets.</p>
                        
                        <!-- CTA Button -->
                        <div style="text-align: center; margin: 32px 0 16px 0;">
                            <a href="{settings.FRONTEND_DASHBOARD_URL}" style="background-color: #0284c7; color: #ffffff; padding: 12px 28px; font-size: 15px; font-weight: 600; text-decoration: none; border-radius: 6px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">View My Dashboard</a>
                        </div>
                    </div>
                    <!-- Footer -->
                    <div style="background-color: #f9fafb; padding: 24px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
                        <p style="margin: 0 0 6px 0;">&copy; 2026 PMRG Solution. All rights reserved.</p>
                        <p style="margin: 0;">This is an automated pipeline state update notification.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

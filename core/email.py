"""
MCSC Transactional Email via Resend
------------------------------------
Provides HTML email sending for grievance lifecycle events.
NEVER raises exceptions — all failures are logged and swallowed so
the site keeps running even if Resend is down or misconfigured.
"""

import logging
from django.conf import settings

logger = logging.getLogger('mcsc.email')

# ─────────────────────────────────────────────────────────────────────────────
# Base HTML template shared by all emails
# ─────────────────────────────────────────────────────────────────────────────

def _base_html(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#005c9b 0%,#0076cc 100%);padding:32px 40px;text-align:center;">
              <div style="display:inline-block;background:rgba(255,255,255,0.15);border-radius:50%;width:56px;height:56px;line-height:56px;margin-bottom:12px;">
                <span style="font-size:28px;">🎓</span>
              </div>
              <h1 style="margin:0;color:#ffffff;font-size:20px;font-weight:700;letter-spacing:0.5px;">Marian College Students Council</h1>
              <p style="margin:4px 0 0;color:rgba(255,255,255,0.75);font-size:12px;text-transform:uppercase;letter-spacing:1.5px;">MCSC Portal</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              {body_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:20px 40px;text-align:center;">
              <p style="margin:0;color:#94a3b8;font-size:12px;">
                This is an automated message from the <strong>MCSC Portal</strong>.<br/>
                Please do not reply to this email.
              </p>
              <p style="margin:8px 0 0;color:#94a3b8;font-size:11px;">
                © 2025 Marian College Students Council, Kuttikkanam
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _status_badge(status: str) -> str:
    """Returns a colored inline badge for a grievance status."""
    colors = {
        'open':      ('#fff7ed', '#c2410c', '#fed7aa'),
        'in-review': ('#eff6ff', '#1d4ed8', '#bfdbfe'),
        'resolved':  ('#f0fdf4', '#15803d', '#bbf7d0'),
    }
    bg, text, border = colors.get(status, ('#f1f5f9', '#475569', '#e2e8f0'))
    labels = {'open': 'Open', 'in-review': 'In Review', 'resolved': 'Resolved'}
    label = labels.get(status, status.title())
    return (
        f'<span style="display:inline-block;padding:4px 14px;border-radius:999px;'
        f'background:{bg};color:{text};border:1px solid {border};'
        f'font-size:12px;font-weight:600;">{label}</span>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Internal send helper
# ─────────────────────────────────────────────────────────────────────────────

def _send(to_email: str, subject: str, html: str) -> bool:
    """
    Send an email via Resend. Returns True on success, False on failure.
    Silently skips if RESEND_API_KEY is not configured.
    NEVER raises — all exceptions are caught and logged.
    """
    try:
        api_key = getattr(settings, 'RESEND_API_KEY', '')
        if not api_key:
            logger.debug('[MCSC Email] RESEND_API_KEY not set — skipping email to %s', to_email)
            return False

        import resend as _resend
        _resend.api_key = api_key
        from_email = getattr(settings, 'RESEND_FROM_EMAIL', 'MCSC Students Council <onboarding@resend.dev>')

        params = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html,
        }
        _resend.Emails.send(params)
        logger.info('[MCSC Email] Sent "%s" to %s', subject, to_email)
        return True
    except Exception as e:
        logger.warning('[MCSC Email] Failed to send "%s" to %s: %s', subject, to_email, e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Public API — one function per email type
# ─────────────────────────────────────────────────────────────────────────────

def send_grievance_submitted(grievance) -> bool:
    """
    Sends a confirmation email to the student when they submit a new grievance.
    NEVER raises — safe to call from signals.
    """
    try:
        student = grievance.student
        name = student.first_name or student.username

        body = f"""
          <h2 style="margin:0 0 8px;color:#1e293b;font-size:22px;font-weight:700;">Grievance Submitted ✅</h2>
          <p style="margin:0 0 24px;color:#64748b;font-size:15px;">Hi {name}, your grievance has been received and is now under review.</p>

          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #005c9b;border-radius:8px;padding:20px 24px;margin-bottom:24px;">
            <p style="margin:0 0 6px;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Grievance Title</p>
            <p style="margin:0 0 16px;color:#1e293b;font-size:16px;font-weight:600;">{grievance.title}</p>

            <p style="margin:0 0 6px;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Category</p>
            <p style="margin:0 0 16px;color:#475569;font-size:14px;">{grievance.get_category_display()}</p>

            <p style="margin:0 0 6px;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Status</p>
            <p style="margin:0;">{_status_badge(grievance.status)}</p>
          </div>

          <p style="color:#64748b;font-size:14px;line-height:1.6;margin:0 0 24px;">
            The MCSC team will review your submission and respond as soon as possible. You will receive an email notification when there is an update.
          </p>

          <p style="color:#94a3b8;font-size:13px;margin:0;">
            Best regards,<br/>
            <strong style="color:#005c9b;">Marian College Students Council</strong>
          </p>
        """

        return _send(
            to_email=student.email,
            subject="Grievance Submitted — MCSC Portal",
            html=_base_html("Grievance Submitted — MCSC", body)
        )
    except Exception as e:
        logger.warning('[MCSC Email] send_grievance_submitted failed: %s', e)
        return False


def send_reply_notification(reply) -> bool:
    """
    Sends an email to the student when an admin posts a reply to their grievance.
    NEVER raises — safe to call from signals.
    """
    try:
        grievance = reply.grievance
        student = grievance.student
        name = student.first_name or student.username
        admin_name = reply.admin.get_full_name() or reply.admin.username

        body = f"""
          <h2 style="margin:0 0 8px;color:#1e293b;font-size:22px;font-weight:700;">New Reply on Your Grievance 💬</h2>
          <p style="margin:0 0 24px;color:#64748b;font-size:15px;">Hi {name}, an MCSC administrator has responded to your grievance.</p>

          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #005c9b;border-radius:8px;padding:20px 24px;margin-bottom:20px;">
            <p style="margin:0 0 6px;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Your Grievance</p>
            <p style="margin:0 0 16px;color:#1e293b;font-size:16px;font-weight:600;">{grievance.title}</p>

            <p style="margin:0 0 6px;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Status</p>
            <p style="margin:0;">{_status_badge(grievance.status)}</p>
          </div>

          <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:20px 24px;margin-bottom:24px;">
            <p style="margin:0 0 6px;color:#1d4ed8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Reply from {admin_name}</p>
            <p style="margin:0;color:#1e293b;font-size:15px;line-height:1.7;white-space:pre-wrap;">{reply.reply_text}</p>
          </div>

          <p style="color:#94a3b8;font-size:13px;margin:0;">
            Best regards,<br/>
            <strong style="color:#005c9b;">Marian College Students Council</strong>
          </p>
        """

        return _send(
            to_email=student.email,
            subject="New Reply on Your Grievance — MCSC Portal",
            html=_base_html("New Reply — MCSC", body)
        )
    except Exception as e:
        logger.warning('[MCSC Email] send_reply_notification failed: %s', e)
        return False


def send_status_update(grievance) -> bool:
    """
    Sends an email to the student when their grievance status is updated.
    NEVER raises — safe to call from signals.
    """
    try:
        student = grievance.student
        name = student.first_name or student.username

        status_messages = {
            'open':      "Your grievance has been reopened and is now in our queue.",
            'in-review': "Your grievance is now being actively reviewed by the MCSC team.",
            'resolved':  "Great news! Your grievance has been marked as resolved.",
        }
        status_msg = status_messages.get(grievance.status, "Your grievance status has been updated.")

        body = f"""
          <h2 style="margin:0 0 8px;color:#1e293b;font-size:22px;font-weight:700;">Grievance Status Updated 🔔</h2>
          <p style="margin:0 0 24px;color:#64748b;font-size:15px;">Hi {name}, the status of your grievance has changed.</p>

          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid #005c9b;border-radius:8px;padding:20px 24px;margin-bottom:20px;">
            <p style="margin:0 0 6px;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Grievance</p>
            <p style="margin:0 0 16px;color:#1e293b;font-size:16px;font-weight:600;">{grievance.title}</p>

            <p style="margin:0 0 6px;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">New Status</p>
            <p style="margin:0;">{_status_badge(grievance.status)}</p>
          </div>

          <p style="color:#475569;font-size:14px;line-height:1.6;margin:0 0 24px;">
            {status_msg}
          </p>

          <p style="color:#94a3b8;font-size:13px;margin:0;">
            Best regards,<br/>
            <strong style="color:#005c9b;">Marian College Students Council</strong>
          </p>
        """

        return _send(
            to_email=student.email,
            subject="Grievance Status Updated — MCSC Portal",
            html=_base_html("Status Updated — MCSC", body)
        )
    except Exception as e:
        logger.warning('[MCSC Email] send_status_update failed: %s', e)
        return False

# Project Requirements

## User Workflow

1. **Access:** User opens the web application (secured via certificate).
2. **MFA:** User completes CAPTCHA and provides email for MFA.
3. **Email Confirmation:** User enters email twice (second field: paste disabled).
4. **Token Verification:** App sends random 5-6 digit token to email, user must enter it to continue.
5. **Form Completion:** User fills in form fields (see [form_fields.md](form_fields.md)).
6. **Signature:** User can type or draw signature (and date).
7. **Submission:** 
    - PDF is generated: `FirstName_LastName_Application_Form_DDMMYYYYHHMM.pdf`
    - PDF sent to both user and company via email.
    - PDF stored in Azure Blob Storage or Google Drive.
8. **Validation:** Dates use date control, countries as dropdown, other input types validated.

## Technical

- **Backend:** Python (FastAPI/Flask/Django)
- **Frontend:** Modern JS framework or simple HTML/JS
- **CI/CD:** GitHub Actions or Azure DevOps for build/deployment
- **Documentation:** Include how to edit graphics, add new fields, and configure CI/CD
- **Deployment:** To be hosted on your Azure domain

## PDF Generation

- Use a Python PDF library (e.g., reportlab, WeasyPrint) to generate the completed form as a PDF.
- Attach and email to both parties, and upload to storage.

## Security

- App must be HTTPS (cert secured)
- CAPTCHA and MFA to prevent spam
- Store sensitive data securely

## Branding

- Customizable graphics/logos (see `branding/` folder)

---

For any questions, see the Issues tab or contact the repo owner.
# Azure Accommodation Application Form

This project will modernize a manual accommodation application form into a secure, user-friendly web application hosted in Azure.

## Project Goals

- Replace paper/email form submission with a secure web app.
- Automate authentication, MFA, and PDF generation.
- Store submissions securely and send confirmations via email.
- Fit the workflow described in the [docs/requirements.md](docs/requirements.md).

## Stack

- **Backend:** Python (FastAPI preferred, Flask/Django acceptable)
- **Frontend:** React/Vue/Angular or plain HTML/JS
- **Hosting:** Azure App Service/Functions, Azure Storage
- **CI/CD:** GitHub Actions

## Getting Started

1. Clone this repo.
2. See [docs/requirements.md](docs/requirements.md) for details.
3. All issues and features are tracked in the Issues tab.

## Developer Notes

- See [docs/form_fields.md](docs/form_fields.md) for the full form structure.
- The initial form is available for frontend implementation in [form_schema.json](form_schema.json).

## Branding

If you have branding assets, place them in the `branding/` folder.

---

**Agent Instructions:**  
- Begin by implementing the form described in [docs/form_fields.md](docs/form_fields.md).
- Follow the requirements in [docs/requirements.md](docs/requirements.md).
- Use best practices for security, Azure deployment, and PDF handling.
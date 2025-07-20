# Azure Accommodation Application Form

This project will modernize a manual accommodation application form into a secure, user-friendly web application hosted in Azure.

## Project Goals

- Replace paper/email form submission with a secure web app.
- Automate authentication, MFA, and PDF generation.
- Store submissions securely and send confirmations via email.
- Fit the workflow described in the [docs/requirements.md](docs/requirements.md).

## Stack

- **Frontend:** React with TypeScript, Vite for build tooling
- **Backend:** Python (FastAPI preferred, Flask/Django acceptable)
- **Hosting:** Azure App Service/Functions, Azure Storage
- **CI/CD:** GitHub Actions

## Frontend Setup

The frontend is built with React, TypeScript, and Vite for fast development and building.

### Prerequisites

- Node.js 18+ 
- npm

### Getting Started

1. Clone this repo
2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at [http://localhost:5173](http://localhost:5173)

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build the app for production
- `npm run preview` - Preview the production build locally
- `npm run lint` - Run ESLint to check code quality

### Project Structure

```
src/
├── App.tsx              # Main app component
├── index.tsx            # App entry point
└── ApplicationFormFields.tsx  # Form implementation
```

### Technologies Used

- **React 18** - UI library with modern hooks
- **TypeScript** - Type safety and better development experience  
- **Vite** - Fast build tool and dev server
- **ESLint** - Code linting and formatting
- **React Hook Form** - Form handling library

## Backend Setup

See [docs/requirements.md](docs/requirements.md) for backend setup details.

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
# Azure Accommodation Application Form

This project provides a secure, user-friendly web application for accommodation applications, with implementations in both **React** and **Blazor (.NET 8 LTS)**.

## Project Goals

- Replace paper/email form submission with a secure web app.
- Automate authentication, MFA, and PDF generation.
- Store submissions securely and send confirmations via email.
- Fit the workflow described in the [docs/requirements.md](docs/requirements.md).

## Available Implementations

### 🆕 Blazor Server (.NET 8 LTS) - **Recommended**
Modern server-side implementation with interactive components.

**Features:**
- Server-side rendering for better performance and SEO
- Interactive server components via SignalR
- Built-in validation with C# models
- Type-safe development with .NET
- Ready for Azure App Service deployment

**Setup:**
```bash
cd BlazorApp
dotnet restore
dotnet build  
dotnet run
```
The app will be available at [http://localhost:5260](http://localhost:5260)

📖 See [BlazorApp/MIGRATION.md](BlazorApp/MIGRATION.md) for migration details and comparison.

### ⚡ React + TypeScript (Legacy)
Original frontend implementation with Vite build tooling.

**Setup:**
```bash
npm install
npm run dev
```
The app will be available at [http://localhost:5173](http://localhost:5173)

## Technology Stacks

### Blazor Implementation
- **Frontend:** Blazor Server with Interactive Server Components
- **Backend:** .NET 8, C# models with validation attributes  
- **Hosting:** Azure App Service
- **Real-time:** SignalR for interactive features

### React Implementation  
- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** Python (FastAPI preferred, Flask/Django acceptable)
- **Hosting:** Azure App Service/Functions, Azure Storage
- **CI/CD:** GitHub Actions

## Form Structure

Both implementations provide identical functionality:

✅ **12 Form Sections:**
1. Tenant Details
2. Bank Details
3. Address History (3 years)
4. Contacts  
5. Medical Details
6. Employment
7. Employment Change
8. Passport Details
9. Current Living Arrangement
10. Other Details
11. Occupation Agreement
12. Consent & Declaration

✅ **Interactive Features:**
- Conditional field visibility
- Dynamic address history addition
- Form validation and submission
- JSON serialization for backend processing

## Available Scripts

### Blazor (.NET 8)
- `dotnet run` - Start the development server
- `dotnet build` - Build the application
- `dotnet test` - Run tests (if any)
- `dotnet publish` - Build for production deployment

### React (Legacy)
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build the app for production  
- `npm run preview` - Preview the production build locally
- `npm run lint` - Run ESLint to check code quality

## Project Structure

```
/
├── BlazorApp/                    # .NET 8 Blazor implementation
│   ├── Components/
│   │   ├── Pages/Home.razor     # Main form component
│   │   └── Layout/              # Layout components
│   ├── Models/FormModels.cs     # C# form models with validation
│   ├── Program.cs               # Application entry point
│   └── MIGRATION.md             # Migration documentation
├── src/                         # React implementation (legacy)
│   ├── App.tsx                  # Main app component
│   ├── index.tsx                # App entry point
│   └── ApplicationFormFields.tsx # Form implementation
├── docs/                        # Documentation
│   ├── requirements.md          # Project requirements
│   └── form_fields.md          # Form structure details
└── form_schema.json            # JSON schema for form data
```

## Backend Integration

The form generates JSON data compatible with both implementations:

```json
{
  "TenantDetails": {
    "FullName": "...",
    "Email": "...",
    // ... other fields
  },
  "BankDetails": { ... },
  "AddressHistory": [ ... ],
  // ... other sections
}
```

## Developer Notes

- See [docs/form_fields.md](docs/form_fields.md) for the complete form structure
- The form schema is defined in [form_schema.json](form_schema.json)
- For Blazor-specific details, see [BlazorApp/MIGRATION.md](BlazorApp/MIGRATION.md)

## Deployment

### Blazor (Recommended)
Deploy to Azure App Service with .NET 8 runtime. The application includes SignalR support for interactive features.

### React (Legacy)  
Deploy frontend to static hosting (Azure Static Web Apps) with separate backend API.

## Branding

If you have branding assets, place them in the `branding/` folder.

---

**Getting Started:**
1. Choose your preferred implementation (Blazor recommended for new development)
2. Follow the setup instructions above
3. Customize the form fields and styling as needed
4. Integrate with your backend API
5. Deploy to Azure
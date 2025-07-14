#!/bin/bash
# Bulk create issues for orkinosai-org/azure-accommodation-form

gh issue create --title "Set up backend project structure (Python FastAPI)" --body "Initialize a FastAPI backend structure with required dependencies." --label "backend,setup"
gh issue create --title "Set up frontend project structure (React)" --body "Initialize a React frontend structure with Create React App or Vite." --label "frontend,setup"
gh issue create --title "Implement email-based multi-factor authentication (MFA) with CAPTCHA" --body "Add MFA with email token and CAPTCHA for user verification." --label "backend,auth"
gh issue create --title "Build the main application form (UI and validation)" --body "Implement the full form UI with validation as per requirements." --label "frontend,form"
gh issue create --title "Implement backend API to receive and process form data" --body "Create endpoints to receive, validate, and process form submissions." --label "backend,api"
gh issue create --title "Generate PDF from submitted form data" --body "Generate a PDF from submitted form using a Python library." --label "backend,pdf"
gh issue create --title "Send PDF via email to user and admin, store in Azure Blob Storage" --body "Email the PDF to user and admin, and store it in Azure Blob Storage." --label "backend,email,azure"
gh issue create --title "Implement signature capture (typed or drawn)" --body "Add functionality to allow users to type or draw their signature in the form." --label "frontend,form,signature"
gh issue create --title "Add CI/CD workflow for automated deployment to Azure" --body "Set up GitHub Actions for CI/CD and deployment to Azure." --label "devops,ci/cd"
gh issue create --title "Write user and developer documentation" --body "Create documentation for both users and developers." --label "documentation"
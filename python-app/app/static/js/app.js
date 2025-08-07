/**
 * Azure Accommodation Form - Frontend JavaScript
 * Handles form workflow, validation, and user interactions
 */

class AzureAccommodationForm {
    constructor() {
        this.currentStep = 1;
        this.sessionToken = null;
        this.verificationId = null;
        this.formData = {};
        this.mathQuestion = '';
        this.mathQuestionTimestamp = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Azure Accommodation Form...');
        
        // Bind event listeners
        this.bindEvents();
        
        // Start certificate verification
        this.verifyCertificate();
    }
    
    bindEvents() {
        // Email verification events
        document.getElementById('send-verification-btn')?.addEventListener('click', () => this.sendEmailVerification());
        document.getElementById('verify-token-btn')?.addEventListener('click', () => this.verifyMFAToken());
        document.getElementById('resend-code-btn')?.addEventListener('click', () => this.resendVerificationCode());
        
        // Form validation
        document.getElementById('email')?.addEventListener('input', (e) => this.validateEmailMatch());
        document.getElementById('email-confirm')?.addEventListener('input', (e) => this.validateEmailMatch());
        
        // Prevent copy-paste on email confirmation
        const emailConfirm = document.getElementById('email-confirm');
        if (emailConfirm) {
            emailConfirm.addEventListener('paste', (e) => {
                e.preventDefault();
                this.showAlert('Copy-paste is disabled for email confirmation. Please type your email again.', 'warning');
            });
            emailConfirm.addEventListener('contextmenu', (e) => e.preventDefault());
        }
        
        // MFA token formatting
        document.getElementById('mfa-token')?.addEventListener('input', (e) => this.formatMFAToken(e));
    }
    
    async verifyCertificate() {
        try {
            this.updateStep(1);
            
            const response = await fetch('/api/auth/verify-certificate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showSuccess('Certificate verification successful');
                setTimeout(() => {
                    this.showEmailVerification();
                }, 1500);
            } else {
                this.showError('Certificate verification failed: ' + result.detail);
            }
        } catch (error) {
            console.error('Certificate verification error:', error);
            this.showError('Certificate verification failed. Please ensure you have a valid client certificate.');
        }
    }
    
    showEmailVerification() {
        this.updateStep(2);
        this.hideSection('certificate-section');
        this.showSection('email-section');
        
        // Initialize Math CAPTCHA
        this.initMathCaptcha();
    }
    
    async initMathCaptcha() {
        try {
            const response = await fetch('/api/auth/generate-math-captcha');
            const result = await response.json();
            
            if (response.ok) {
                this.mathQuestion = result.question;
                this.mathQuestionTimestamp = result.timestamp;
                
                // Update the UI with the math question
                const questionElement = document.getElementById('math-question');
                if (questionElement) {
                    questionElement.textContent = result.question;
                }
                
                // Clear any previous answer
                const answerElement = document.getElementById('math-answer');
                if (answerElement) {
                    answerElement.value = '';
                }
            } else {
                console.error('Failed to generate math captcha:', result);
                this.showError('Failed to load security verification. Please refresh the page.');
            }
        } catch (error) {
            console.error('Error initializing math captcha:', error);
            this.showError('Failed to load security verification. Please refresh the page.');
        }
    }
    
    validateEmailMatch() {
        const email = document.getElementById('email').value;
        const emailConfirm = document.getElementById('email-confirm').value;
        
        const emailConfirmField = document.getElementById('email-confirm');
        
        if (emailConfirm && email !== emailConfirm) {
            emailConfirmField.classList.add('is-invalid');
            emailConfirmField.classList.remove('is-valid');
        } else if (emailConfirm) {
            emailConfirmField.classList.add('is-valid');
            emailConfirmField.classList.remove('is-invalid');
        }
    }
    
    async sendEmailVerification() {
        const email = document.getElementById('email').value;
        const emailConfirm = document.getElementById('email-confirm').value;
        
        // Validation
        if (!email || !emailConfirm) {
            this.showAlert('Please enter and confirm your email address.', 'warning');
            return;
        }
        
        if (email !== emailConfirm) {
            this.showAlert('Email addresses do not match.', 'danger');
            return;
        }
        
        // Get Math CAPTCHA answer
        const mathAnswer = document.getElementById('math-answer').value;
        
        if (!mathAnswer || isNaN(mathAnswer)) {
            this.showAlert('Please answer the security question.', 'warning');
            return;
        }
        
        if (!this.mathQuestion) {
            this.showAlert('Security question not loaded. Please refresh the page.', 'warning');
            return;
        }
        
        try {
            this.showLoading('Sending verification code...');
            
            const response = await fetch('/api/auth/request-email-verification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    email_confirm: emailConfirm,
                    math_question: this.mathQuestion,
                    math_answer: parseInt(mathAnswer)
                })
            });
            
            const result = await response.json();
            this.hideLoading();
            
            if (response.ok) {
                this.verificationId = result.verification_id;
                this.showMFATokenForm();
                this.startTokenTimer(result.expires_at);
                this.showSuccess(result.message);
            } else {
                this.showError(result.detail);
                
                // Generate new math question on failure
                this.initMathCaptcha();
            }
        } catch (error) {
            this.hideLoading();
            console.error('Email verification error:', error);
            this.showError('Failed to send verification code. Please try again.');
        }
    }
    
    showMFATokenForm() {
        document.getElementById('email-entry-form').classList.add('d-none');
        document.getElementById('mfa-token-form').classList.remove('d-none');
        document.getElementById('mfa-token').focus();
    }
    
    formatMFAToken(event) {
        let value = event.target.value.replace(/\D/g, ''); // Remove non-digits
        if (value.length > 6) value = value.substring(0, 6);
        event.target.value = value;
    }
    
    async verifyMFAToken() {
        const token = document.getElementById('mfa-token').value;
        
        if (!token || token.length !== 6) {
            this.showAlert('Please enter the complete 6-digit verification code.', 'warning');
            return;
        }
        
        try {
            this.showLoading('Verifying code...');
            
            const response = await fetch('/api/auth/verify-mfa-token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    verification_id: this.verificationId,
                    token: token
                })
            });
            
            const result = await response.json();
            this.hideLoading();
            
            if (response.ok && result.verified) {
                this.sessionToken = result.session_token;
                this.showSuccess('Email verification successful!');
                setTimeout(() => {
                    this.showApplicationForm();
                }, 1500);
            } else {
                this.showError(result.message || 'Invalid verification code');
                document.getElementById('mfa-token').value = '';
                document.getElementById('mfa-token').focus();
            }
        } catch (error) {
            this.hideLoading();
            console.error('MFA verification error:', error);
            this.showError('Failed to verify code. Please try again.');
        }
    }
    
    async resendVerificationCode() {
        // Reset to email entry form
        document.getElementById('mfa-token-form').classList.add('d-none');
        document.getElementById('email-entry-form').classList.remove('d-none');
        
        // Generate new math question
        await this.initMathCaptcha();
        
        this.showAlert('Please answer the security question again to resend the verification code.', 'info');
    }
    
    startTokenTimer(expiresAt) {
        const expiryTime = new Date(expiresAt);
        const timerElement = document.getElementById('token-timer');
        
        const updateTimer = () => {
            const now = new Date();
            const timeLeft = expiryTime - now;
            
            if (timeLeft <= 0) {
                timerElement.innerHTML = '<span class="text-danger">Verification code has expired</span>';
                return;
            }
            
            const minutes = Math.floor(timeLeft / 60000);
            const seconds = Math.floor((timeLeft % 60000) / 1000);
            
            timerElement.innerHTML = `Code expires in: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        };
        
        updateTimer();
        const interval = setInterval(updateTimer, 1000);
        
        setTimeout(() => clearInterval(interval), 10 * 60 * 1000); // Clear after 10 minutes
    }
    
    async showApplicationForm() {
        this.updateStep(3);
        this.hideSection('email-section');
        this.showSection('form-section');
        
        try {
            // Initialize form session
            const response = await fetch('/api/form/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-Token': this.sessionToken
                }
            });
            
            if (response.ok) {
                await this.loadFormContent();
            } else {
                throw new Error('Failed to initialize form session');
            }
        } catch (error) {
            console.error('Form initialization error:', error);
            this.showError('Failed to load application form. Please try again.');
        }
    }
    
    async loadFormContent() {
        // Load the main form content
        const formContainer = document.getElementById('accommodation-form');
        document.getElementById('form-loading').style.display = 'none';
        
        // Generate form HTML based on schema
        const formHTML = await this.generateFormHTML();
        formContainer.innerHTML = formHTML;
        
        // Bind form events
        this.bindFormEvents();
    }
    
    async generateFormHTML() {
        // Generate comprehensive form HTML that matches the backend model
        return `
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        Please fill out all required fields marked with an asterisk (*).
                    </div>
                </div>
            </div>
            
            <!-- Tenant Details Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">1. Tenant Details</h4>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="full_name" class="form-label">Full Name *</label>
                            <input type="text" class="form-control" id="full_name" name="full_name" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="date_of_birth" class="form-label">Date of Birth *</label>
                            <input type="date" class="form-control" id="date_of_birth" name="date_of_birth" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="place_of_birth" class="form-label">Place of Birth *</label>
                            <input type="text" class="form-control" id="place_of_birth" name="place_of_birth" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="email_readonly" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email_readonly" readonly>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="telephone" class="form-label">Telephone *</label>
                            <input type="tel" class="form-control" id="telephone" name="telephone" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="employers_name" class="form-label">Employer's Name *</label>
                            <input type="text" class="form-control" id="employers_name" name="employers_name" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="gender" class="form-label">Gender *</label>
                            <select class="form-control" id="gender" name="gender" required>
                                <option value="">Select Gender</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="ni_number" class="form-label">National Insurance Number *</label>
                            <input type="text" class="form-control" id="ni_number" name="ni_number" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="room_occupancy" class="form-label">Room Occupancy *</label>
                            <select class="form-control" id="room_occupancy" name="room_occupancy" required>
                                <option value="">Select Occupancy</option>
                                <option value="just_you">Just You</option>
                                <option value="you_and_someone_else">You and Someone Else</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="right_to_live_in_uk" name="right_to_live_in_uk">
                                <label class="form-check-label" for="right_to_live_in_uk">
                                    Right to Live in UK *
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="car" name="car">
                                <label class="form-check-label" for="car">
                                    Do you have a car?
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="bicycle" name="bicycle">
                                <label class="form-check-label" for="bicycle">
                                    Do you have a bicycle?
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bank Details Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">2. Bank Details</h4>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="bank_name" class="form-label">Bank Name *</label>
                            <input type="text" class="form-control" id="bank_name" name="bank_name" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="bank_postcode" class="form-label">Bank Postcode *</label>
                            <input type="text" class="form-control" id="bank_postcode" name="bank_postcode" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="account_no" class="form-label">Account Number *</label>
                            <input type="text" class="form-control" id="account_no" name="account_no" maxlength="8" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="sort_code" class="form-label">Sort Code *</label>
                            <input type="text" class="form-control" id="sort_code" name="sort_code" placeholder="12-34-56" required>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Address History Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">3. Address History</h4>
                <div id="address-history-container">
                    <div class="address-entry mb-3 border p-3 rounded">
                        <h6>Current Address</h6>
                        <div class="row">
                            <div class="col-md-8">
                                <div class="mb-3">
                                    <label for="address_0" class="form-label">Address *</label>
                                    <textarea class="form-control" id="address_0" name="address_0" rows="2" required></textarea>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="from_date_0" class="form-label">From Date *</label>
                                    <input type="date" class="form-control" id="from_date_0" name="from_date_0" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_name_0" class="form-label">Landlord Name *</label>
                                    <input type="text" class="form-control" id="landlord_name_0" name="landlord_name_0" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_tel_0" class="form-label">Landlord Tel *</label>
                                    <input type="tel" class="form-control" id="landlord_tel_0" name="landlord_tel_0" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_email_0" class="form-label">Landlord Email *</label>
                                    <input type="email" class="form-control" id="landlord_email_0" name="landlord_email_0" required>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Simplified form for minimal testing -->
            <div class="form-section mb-4">
                <h4 class="section-title">4. Quick Test Form</h4>
                <p class="text-muted">Simplified form for testing purposes</p>
                
                <!-- Minimal required fields for other sections -->
                <input type="hidden" id="contacts_data" value='{"next_of_kin":"Test Contact","relationship":"Friend","address":"Test Address","contact_number":"1234567890"}'>
                <input type="hidden" id="medical_data" value='{"gp_practice":"Test Practice","doctor_name":"Dr. Test","doctor_address":"Test Address","doctor_telephone":"1234567890"}'>
                <input type="hidden" id="employment_data" value='{"employer_name_address":"Test Employer","job_title":"Test Job","manager_name":"Test Manager","manager_tel":"1234567890","manager_email":"test@example.com","date_of_employment":"2023-01-01","present_salary":30000}'>
                <input type="hidden" id="passport_data" value='{"passport_number":"TEST123456","date_of_issue":"2023-01-01","place_of_issue":"Test Location"}'>
                <input type="hidden" id="living_data" value='{"landlord_knows":true,"reason_leaving":"Test reason","landlord_reference":true,"landlord_contact":{"name":"Test Landlord","address":"Test Address","tel":"1234567890","email":"landlord@example.com"}}'>
                <input type="hidden" id="other_data" value='{"pets_has":false,"smoke":false,"coliving_has":false}'>
                <input type="hidden" id="agreement_data" value='{"single_occupancy_agree":true,"hmo_terms_agree":true,"no_unlisted_occupants":true,"no_smoking":true,"kitchen_cooking_only":true}'>
                <input type="hidden" id="consent_data" value='{"consent_given":true,"signature":"Test Signature","date":"2024-01-01","print_name":"Test Name","declaration":{"main_home":true,"enquiries_permission":true,"certify_no_judgements":true,"certify_no_housing_debt":true,"certify_no_landlord_debt":true,"certify_no_abuse":true},"declaration_signature":"Test Signature","declaration_date":"2024-01-01","declaration_print_name":"Test Name"}'>
            </div>
            
            <!-- Submit Section -->
            <div class="form-section">
                <div class="row">
                    <div class="col-12">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-paper-plane me-2"></i>
                            Submit Application
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindFormEvents() {
        // Set readonly email from verification
        const emailField = document.getElementById('email_readonly');
        if (emailField) {
            emailField.value = document.getElementById('email').value;
        }
        
        // Set default signature date
        const signatureDateField = document.getElementById('signature_date');
        if (signatureDateField) {
            signatureDateField.value = new Date().toISOString().split('T')[0];
        }
        
        // Signature type toggle
        document.querySelectorAll('input[name="signature_type"]').forEach(radio => {
            radio.addEventListener('change', () => this.toggleSignatureType());
        });
        
        // Form submission
        document.getElementById('accommodation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });
        
        // Initialize signature pad if needed
        this.initSignaturePad();
    }
    
    toggleSignatureType() {
        const typedSection = document.getElementById('typed-signature-section');
        const drawnSection = document.getElementById('drawn-signature-section');
        const isTyped = document.getElementById('signature_typed').checked;
        
        if (isTyped) {
            typedSection.classList.remove('d-none');
            drawnSection.classList.add('d-none');
        } else {
            typedSection.classList.add('d-none');
            drawnSection.classList.remove('d-none');
        }
    }
    
    initSignaturePad() {
        // Initialize signature pad functionality
        const canvas = document.getElementById('signature-pad');
        const clearBtn = document.getElementById('clear-signature');
        
        if (canvas) {
            const ctx = canvas.getContext('2d');
            let isDrawing = false;
            
            canvas.addEventListener('mousedown', (e) => {
                isDrawing = true;
                ctx.beginPath();
                const rect = canvas.getBoundingClientRect();
                ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
            });
            
            canvas.addEventListener('mousemove', (e) => {
                if (!isDrawing) return;
                const rect = canvas.getBoundingClientRect();
                ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
                ctx.stroke();
            });
            
            canvas.addEventListener('mouseup', () => {
                isDrawing = false;
            });
            
            clearBtn?.addEventListener('click', () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            });
        }
    }
    
    async submitForm() {
        try {
            this.showLoading('Submitting application...');
            this.updateStep(4);
            
            // Collect form data
            const formData = this.collectFormData();
            
            // Submit to server
            const response = await fetch('/api/form/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-Token': this.sessionToken
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            this.hideLoading();
            
            if (response.ok) {
                this.showSubmissionSuccess(result);
            } else {
                this.showError(result.detail || 'Form submission failed');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Form submission error:', error);
            this.showError('Failed to submit form. Please try again.');
        }
    }
    
    collectFormData() {
        // Collect comprehensive form data that matches the backend model
        return {
            tenant_details: {
                full_name: document.getElementById('full_name')?.value || '',
                date_of_birth: document.getElementById('date_of_birth')?.value || '',
                place_of_birth: document.getElementById('place_of_birth')?.value || '',
                email: document.getElementById('email_readonly')?.value || '',
                telephone: document.getElementById('telephone')?.value || '',
                employers_name: document.getElementById('employers_name')?.value || '',
                gender: document.getElementById('gender')?.value || 'other',
                ni_number: document.getElementById('ni_number')?.value || '',
                car: document.getElementById('car')?.checked || false,
                bicycle: document.getElementById('bicycle')?.checked || false,
                right_to_live_in_uk: document.getElementById('right_to_live_in_uk')?.checked || false,
                room_occupancy: document.getElementById('room_occupancy')?.value || 'just_you',
                other_names_has: false,
                other_names_details: null,
                medical_condition_has: false,
                medical_condition_details: null
            },
            bank_details: {
                bank_name: document.getElementById('bank_name')?.value || '',
                postcode: document.getElementById('bank_postcode')?.value || '',
                account_no: document.getElementById('account_no')?.value || '',
                sort_code: document.getElementById('sort_code')?.value || ''
            },
            address_history: [
                {
                    address: document.getElementById('address_0')?.value || '',
                    from_date: document.getElementById('from_date_0')?.value || '',
                    to_date: null, // Current address
                    landlord_name: document.getElementById('landlord_name_0')?.value || '',
                    landlord_tel: document.getElementById('landlord_tel_0')?.value || '',
                    landlord_email: document.getElementById('landlord_email_0')?.value || ''
                }
            ],
            contacts: JSON.parse(document.getElementById('contacts_data')?.value || '{}'),
            medical_details: JSON.parse(document.getElementById('medical_data')?.value || '{}'),
            employment: JSON.parse(document.getElementById('employment_data')?.value || '{}'),
            employment_change: null,
            passport_details: JSON.parse(document.getElementById('passport_data')?.value || '{}'),
            current_living_arrangement: JSON.parse(document.getElementById('living_data')?.value || '{}'),
            other_details: JSON.parse(document.getElementById('other_data')?.value || '{}'),
            occupation_agreement: JSON.parse(document.getElementById('agreement_data')?.value || '{}'),
            consent_and_declaration: JSON.parse(document.getElementById('consent_data')?.value || '{}'),
            client_ip: null, // Will be set by backend
            form_opened_at: null,
            form_submitted_at: null
        };
    }
    
    showSubmissionSuccess(result) {
        this.hideSection('form-section');
        this.showSection('submission-section');
        
        const detailsDiv = document.getElementById('submission-details');
        detailsDiv.innerHTML = `
            <p><strong>Submission ID:</strong> ${result.submission_id}</p>
            <p><strong>PDF Generated:</strong> ${result.pdf_filename}</p>
            <p><strong>Submitted:</strong> ${new Date(result.timestamp).toLocaleString()}</p>
            <p>A confirmation email with your application PDF has been sent to your email address.</p>
        `;
    }
    
    // Utility methods
    updateStep(step) {
        this.currentStep = step;
        
        // Update progress indicators
        for (let i = 1; i <= 4; i++) {
            const stepElement = document.getElementById(`step-${i}`);
            if (stepElement) {
                stepElement.classList.remove('active', 'completed');
                
                if (i < step) {
                    stepElement.classList.add('completed');
                } else if (i === step) {
                    stepElement.classList.add('active');
                }
            }
        }
    }
    
    showSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.remove('d-none');
            section.classList.add('fade-in');
        }
    }
    
    hideSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('d-none');
        }
    }
    
    showAlert(message, type = 'info') {
        // Create and show alert
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insert at top of current visible section
        const currentSection = this.getCurrentSection();
        if (currentSection) {
            currentSection.insertAdjacentHTML('afterbegin', alertHTML);
        }
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showLoading(message = 'Loading...') {
        const loadingHTML = `
            <div class="loading-overlay" id="loading-overlay">
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 mb-0">${message}</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    getCurrentSection() {
        const sections = ['certificate-section', 'email-section', 'form-section', 'submission-section'];
        
        for (const sectionId of sections) {
            const section = document.getElementById(sectionId);
            if (section && !section.classList.contains('d-none')) {
                return section;
            }
        }
        
        return null;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.accommodationForm = new AzureAccommodationForm();
});
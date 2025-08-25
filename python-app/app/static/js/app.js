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
                            <label class="form-label">Right to Live in UK *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="right_to_live_in_uk" id="right_to_live_in_uk_yes" value="true" required>
                                <label class="form-check-label" for="right_to_live_in_uk_yes">
                                    Yes
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="right_to_live_in_uk" id="right_to_live_in_uk_no" value="false" required>
                                <label class="form-check-label" for="right_to_live_in_uk_no">
                                    No
                                </label>
                            </div>
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
                            <label for="bank_branch_address" class="form-label">Bank Branch Address *</label>
                            <textarea class="form-control" id="bank_branch_address" name="bank_branch_address" rows="2" required></textarea>
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
                <h4 class="section-title">3. Address History (Last five years)</h4>
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
                                    <label for="landlord_name_0" class="form-label">Landlord/Agent Name *</label>
                                    <input type="text" class="form-control" id="landlord_name_0" name="landlord_name_0" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_tel_0" class="form-label">Landlord/Agent Tel *</label>
                                    <input type="tel" class="form-control" id="landlord_tel_0" name="landlord_tel_0" required>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_email_0" class="form-label">Landlord/Agent Email *</label>
                                    <input type="email" class="form-control" id="landlord_email_0" name="landlord_email_0" required>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Does landlord know you are leaving? *</label>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="landlord_knows_0" id="landlord_knows_0_yes" value="true" required>
                                        <label class="form-check-label" for="landlord_knows_0_yes">Yes</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="landlord_knows_0" id="landlord_knows_0_no" value="false" required>
                                        <label class="form-check-label" for="landlord_knows_0_no">No</label>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Will landlord give reference? *</label>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="landlord_reference_0" id="landlord_reference_0_yes" value="true" required>
                                        <label class="form-check-label" for="landlord_reference_0_yes">Yes</label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="landlord_reference_0" id="landlord_reference_0_no" value="false" required>
                                        <label class="form-check-label" for="landlord_reference_0_no">No</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="notice_end_date_0" class="form-label">Notice End Date</label>
                                    <input type="date" class="form-control" id="notice_end_date_0" name="notice_end_date_0">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="reason_leaving_0" class="form-label">Reason for wanting to leave *</label>
                                    <textarea class="form-control" id="reason_leaving_0" name="reason_leaving_0" rows="2" required></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Previous Address 1 -->
                    <div class="address-entry mb-3 border p-3 rounded">
                        <h6>Previous Address 1</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="address_1" class="form-label">Address</label>
                                    <textarea class="form-control" id="address_1" name="address_1" rows="2"></textarea>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="mb-3">
                                    <label for="from_date_1" class="form-label">From Date</label>
                                    <input type="date" class="form-control" id="from_date_1" name="from_date_1">
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="mb-3">
                                    <label for="to_date_1" class="form-label">To Date</label>
                                    <input type="date" class="form-control" id="to_date_1" name="to_date_1">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_name_1" class="form-label">Landlord/Agent Name</label>
                                    <input type="text" class="form-control" id="landlord_name_1" name="landlord_name_1">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_tel_1" class="form-label">Landlord/Agent Tel</label>
                                    <input type="tel" class="form-control" id="landlord_tel_1" name="landlord_tel_1">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_email_1" class="form-label">Landlord/Agent Email</label>
                                    <input type="email" class="form-control" id="landlord_email_1" name="landlord_email_1">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-12">
                                <div class="mb-3">
                                    <label for="reason_leaving_1" class="form-label">Reason for leaving</label>
                                    <textarea class="form-control" id="reason_leaving_1" name="reason_leaving_1" rows="2"></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Previous Address 2 -->
                    <div class="address-entry mb-3 border p-3 rounded">
                        <h6>Previous Address 2</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="address_2" class="form-label">Address</label>
                                    <textarea class="form-control" id="address_2" name="address_2" rows="2"></textarea>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="mb-3">
                                    <label for="from_date_2" class="form-label">From Date</label>
                                    <input type="date" class="form-control" id="from_date_2" name="from_date_2">
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="mb-3">
                                    <label for="to_date_2" class="form-label">To Date</label>
                                    <input type="date" class="form-control" id="to_date_2" name="to_date_2">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_name_2" class="form-label">Landlord/Agent Name</label>
                                    <input type="text" class="form-control" id="landlord_name_2" name="landlord_name_2">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_tel_2" class="form-label">Landlord/Agent Tel</label>
                                    <input type="tel" class="form-control" id="landlord_tel_2" name="landlord_tel_2">
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="mb-3">
                                    <label for="landlord_email_2" class="form-label">Landlord/Agent Email</label>
                                    <input type="email" class="form-control" id="landlord_email_2" name="landlord_email_2">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-12">
                                <div class="mb-3">
                                    <label for="reason_leaving_2" class="form-label">Reason for leaving</label>
                                    <textarea class="form-control" id="reason_leaving_2" name="reason_leaving_2" rows="2"></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Emergency Contacts Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">4. Emergency Contacts</h4>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="next_of_kin" class="form-label">Next of Kin *</label>
                            <input type="text" class="form-control" id="next_of_kin" name="next_of_kin" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="relationship" class="form-label">Relationship *</label>
                            <input type="text" class="form-control" id="relationship" name="relationship" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-8">
                        <div class="mb-3">
                            <label for="contact_address" class="form-label">Address *</label>
                            <textarea class="form-control" id="contact_address" name="contact_address" rows="2" required></textarea>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="contact_number" class="form-label">Contact Number *</label>
                            <input type="tel" class="form-control" id="contact_number" name="contact_number" required>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Medical Details Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">5. Medical Details</h4>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="gp_practice" class="form-label">GP Practice *</label>
                            <input type="text" class="form-control" id="gp_practice" name="gp_practice" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="doctor_name" class="form-label">Doctor's Name *</label>
                            <input type="text" class="form-control" id="doctor_name" name="doctor_name" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-8">
                        <div class="mb-3">
                            <label for="doctor_address" class="form-label">Doctor's Address *</label>
                            <textarea class="form-control" id="doctor_address" name="doctor_address" rows="2" required></textarea>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="doctor_telephone" class="form-label">Doctor's Telephone *</label>
                            <input type="tel" class="form-control" id="doctor_telephone" name="doctor_telephone" required>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Employment Details Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">6. Employment Details</h4>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="employers_name" class="form-label">Employer's Name *</label>
                            <input type="text" class="form-control" id="employers_name" name="employers_name" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="job_title" class="form-label">Job Title *</label>
                            <input type="text" class="form-control" id="job_title" name="job_title" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <div class="mb-3">
                            <label for="employer_name_address" class="form-label">Employer Name & Address *</label>
                            <textarea class="form-control" id="employer_name_address" name="employer_name_address" rows="3" required></textarea>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="manager_name" class="form-label">Manager's Name *</label>
                            <input type="text" class="form-control" id="manager_name" name="manager_name" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="manager_tel" class="form-label">Manager's Telephone *</label>
                            <input type="tel" class="form-control" id="manager_tel" name="manager_tel" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="manager_email" class="form-label">Manager's Email *</label>
                            <input type="email" class="form-control" id="manager_email" name="manager_email" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="date_of_employment" class="form-label">Date of Employment *</label>
                            <input type="date" class="form-control" id="date_of_employment" name="date_of_employment" required>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="present_salary" class="form-label">Present Salary (£) *</label>
                            <input type="number" class="form-control" id="present_salary" name="present_salary" min="0" step="1000" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="employment_change" class="form-label">Are circumstances likely to change?</label>
                            <textarea class="form-control" id="employment_change" name="employment_change" rows="2" placeholder="Optional - explain any expected changes"></textarea>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Passport Details Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">7. Passport Details</h4>
                <div class="row">
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="passport_number" class="form-label">Passport Number *</label>
                            <input type="text" class="form-control" id="passport_number" name="passport_number" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="passport_date_of_issue" class="form-label">Date of Issue *</label>
                            <input type="date" class="form-control" id="passport_date_of_issue" name="passport_date_of_issue" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="passport_place_of_issue" class="form-label">Place of Issue *</label>
                            <input type="text" class="form-control" id="passport_place_of_issue" name="passport_place_of_issue" required>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Other Details Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">8. Other Details</h4>
                <div class="row">
                    <div class="col-md-6">
                        <!-- Smoking Question -->
                        <div class="mb-3">
                            <label class="form-label">Do you smoke? *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="smoke" id="smoke_yes" value="true" required>
                                <label class="form-check-label" for="smoke_yes">Yes</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="smoke" id="smoke_no" value="false" required>
                                <label class="form-check-label" for="smoke_no">No</label>
                            </div>
                        </div>
                        <div id="smoke-details-section" style="display: none;">
                            <div class="mb-3">
                                <label for="smoke_details" class="form-label">Please specify</label>
                                <textarea class="form-control" id="smoke_details" name="smoke_details" rows="2" placeholder="Please specify smoking details"></textarea>
                            </div>
                        </div>

                        <!-- Vaping Question -->
                        <div class="mb-3">
                            <label class="form-label">Do you vape? *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="vaping" id="vaping_yes" value="true" required>
                                <label class="form-check-label" for="vaping_yes">Yes</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="vaping" id="vaping_no" value="false" required>
                                <label class="form-check-label" for="vaping_no">No</label>
                            </div>
                        </div>
                        <div id="vaping-details-section" style="display: none;">
                            <div class="mb-3">
                                <label for="vaping_details" class="form-label">Please specify</label>
                                <textarea class="form-control" id="vaping_details" name="vaping_details" rows="2" placeholder="Please specify vaping details"></textarea>
                            </div>
                        </div>

                        <!-- Pets Question -->
                        <div class="mb-3">
                            <label class="form-label">Do you have pets? *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="pets_has" id="pets_has_yes" value="true" required>
                                <label class="form-check-label" for="pets_has_yes">Yes</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="pets_has" id="pets_has_no" value="false" required>
                                <label class="form-check-label" for="pets_has_no">No</label>
                            </div>
                        </div>
                        <div id="pets-details-section" style="display: none;">
                            <div class="mb-3">
                                <label for="pets_details" class="form-label">Pet Details *</label>
                                <textarea class="form-control" id="pets_details" name="pets_details" rows="2" placeholder="Please describe your pets" required></textarea>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <!-- Co-living Question -->
                        <div class="mb-3">
                            <label class="form-label">Do you have co-living preferences? *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="coliving_has" id="coliving_has_yes" value="true" required>
                                <label class="form-check-label" for="coliving_has_yes">Yes</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="coliving_has" id="coliving_has_no" value="false" required>
                                <label class="form-check-label" for="coliving_has_no">No</label>
                            </div>
                        </div>
                        <div id="coliving-details-section" style="display: none;">
                            <div class="mb-3">
                                <label for="coliving_details" class="form-label">Co-living Details *</label>
                                <textarea class="form-control" id="coliving_details" name="coliving_details" rows="2" placeholder="Please describe your preferences" required></textarea>
                            </div>
                        </div>

                        <!-- Medical condition question -->
                        <div class="mb-3">
                            <label class="form-label">Do you have any medical conditions other residents need to know about? *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="medical_condition_has" id="medical_condition_has_yes" value="true" required>
                                <label class="form-check-label" for="medical_condition_has_yes">Yes</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="medical_condition_has" id="medical_condition_has_no" value="false" required>
                                <label class="form-check-label" for="medical_condition_has_no">No</label>
                            </div>
                        </div>
                        <div id="medical-condition-details-section" style="display: none;">
                            <div class="mb-3">
                                <label for="medical_condition_details" class="form-label">Please specify *</label>
                                <textarea class="form-control" id="medical_condition_details" name="medical_condition_details" rows="2" placeholder="Please provide details" required></textarea>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Occupation Agreement Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">9. Occupation Agreement</h4>
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Please read and agree to the following terms and conditions:
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Do you agree to single occupancy terms? *</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="single_occupancy_agree" id="single_occupancy_agree_yes" value="true" required>
                        <label class="form-check-label" for="single_occupancy_agree_yes">Yes</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="single_occupancy_agree" id="single_occupancy_agree_no" value="false" required>
                        <label class="form-check-label" for="single_occupancy_agree_no">No</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Do you agree to HMO terms and conditions? *</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="hmo_terms_agree" id="hmo_terms_agree_yes" value="true" required>
                        <label class="form-check-label" for="hmo_terms_agree_yes">Yes</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="hmo_terms_agree" id="hmo_terms_agree_no" value="false" required>
                        <label class="form-check-label" for="hmo_terms_agree_no">No</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Do you agree not to allow unlisted occupants? *</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="no_unlisted_occupants" id="no_unlisted_occupants_yes" value="true" required>
                        <label class="form-check-label" for="no_unlisted_occupants_yes">Yes</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="no_unlisted_occupants" id="no_unlisted_occupants_no" value="false" required>
                        <label class="form-check-label" for="no_unlisted_occupants_no">No</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Do you agree to the no smoking policy? *</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="no_smoking_agree" id="no_smoking_agree_yes" value="true" required>
                        <label class="form-check-label" for="no_smoking_agree_yes">Yes</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="no_smoking_agree" id="no_smoking_agree_no" value="false" required>
                        <label class="form-check-label" for="no_smoking_agree_no">No</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Do you agree to use the kitchen for cooking only? *</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="kitchen_cooking_only" id="kitchen_cooking_only_yes" value="true" required>
                        <label class="form-check-label" for="kitchen_cooking_only_yes">Yes</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="kitchen_cooking_only" id="kitchen_cooking_only_no" value="false" required>
                        <label class="form-check-label" for="kitchen_cooking_only_no">No</label>
                    </div>
                </div>
            </div>

            <!-- Document Libraries Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">10. Document Libraries (Optional)</h4>
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Select any external document libraries you may need access to for accommodation-related documents.
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Available Document Libraries</label>
                    <div id="library-selector-container" class="mb-3">
                        <!-- Library selector will be loaded here -->
                        <div class="text-center text-muted">
                            <div class="spinner-border spinner-border-sm me-2" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            Loading available libraries...
                        </div>
                    </div>
                </div>
                
                <div id="selected-libraries" class="mb-3" style="display: none;">
                    <label class="form-label">Selected Libraries</label>
                    <div id="selected-libraries-list">
                        <!-- Selected libraries will be displayed here -->
                    </div>
                </div>
            </div>

            <!-- Consent & Declaration Section -->
            <div class="form-section mb-4">
                <h4 class="section-title">11. Consent & Declaration</h4>
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Please read carefully and complete all declaration fields.
                </div>
                
                <!-- Data Processing Consent -->
                <div class="form-check mb-4">
                    <input class="form-check-input" type="checkbox" id="consent_given" name="consent_given" required>
                    <label class="form-check-label" for="consent_given">
                        I consent to the processing of my personal data in accordance with data protection regulations *
                    </label>
                </div>

                <!-- Signature Section -->
                <div class="row">
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="signature" class="form-label">Signature *</label>
                            <input type="text" class="form-control" id="signature" name="signature" placeholder="Type your full name" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="signature_date" class="form-label">Date *</label>
                            <input type="date" class="form-control" id="signature_date" name="signature_date" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="print_name" class="form-label">Print Name *</label>
                            <input type="text" class="form-control" id="print_name" name="print_name" required>
                        </div>
                    </div>
                </div>

                <!-- Declaration Checkboxes -->
                <h6 class="mt-4">Declaration</h6>
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" id="main_home" name="main_home" required>
                    <label class="form-check-label" for="main_home">
                        This will be my main home *
                    </label>
                </div>
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" id="enquiries_permission" name="enquiries_permission" required>
                    <label class="form-check-label" for="enquiries_permission">
                        I give permission for enquiries to be made about me *
                    </label>
                </div>
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" id="certify_no_judgements" name="certify_no_judgements" required>
                    <label class="form-check-label" for="certify_no_judgements">
                        I certify I have no outstanding county court judgements *
                    </label>
                </div>
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" id="certify_no_housing_debt" name="certify_no_housing_debt" required>
                    <label class="form-check-label" for="certify_no_housing_debt">
                        I certify I have no housing-related debt *
                    </label>
                </div>
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" id="certify_no_landlord_debt" name="certify_no_landlord_debt" required>
                    <label class="form-check-label" for="certify_no_landlord_debt">
                        I certify I have no debt to previous landlords *
                    </label>
                </div>
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" id="certify_no_abuse" name="certify_no_abuse" required>
                    <label class="form-check-label" for="certify_no_abuse">
                        I certify I have no history of property abuse *
                    </label>
                </div>
                <div class="form-check mb-4">
                    <input class="form-check-input" type="checkbox" id="certify_no_alcohol_substance_abuse" name="certify_no_alcohol_substance_abuse" required>
                    <label class="form-check-label" for="certify_no_alcohol_substance_abuse">
                        I certify I have no history of alcohol or substance abuse *
                    </label>
                </div>

                <!-- Declaration Signature -->
                <div class="row">
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="declaration_signature" class="form-label">Declaration Signature *</label>
                            <input type="text" class="form-control" id="declaration_signature" name="declaration_signature" placeholder="Type your full name" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="declaration_date" class="form-label">Declaration Date *</label>
                            <input type="date" class="form-control" id="declaration_date" name="declaration_date" required>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label for="declaration_print_name" class="form-label">Declaration Print Name *</label>
                            <input type="text" class="form-control" id="declaration_print_name" name="declaration_print_name" required>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Submit Section -->
            <div class="form-section">
                <div class="row">
                    <div class="col-12">
                        <button type="submit" class="btn btn-secondary btn-lg" disabled>
                            <i class="fas fa-paper-plane me-2"></i>
                            Submit Application
                        </button>
                        <div class="form-text mt-2">
                            <small><i class="fas fa-info-circle me-1"></i>Button will be enabled when all required fields are completed correctly.</small>
                        </div>
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
        
        // Set default dates to today
        const signatureDateField = document.getElementById('signature_date');
        const declarationDateField = document.getElementById('declaration_date');
        const today = new Date().toISOString().split('T')[0];
        
        if (signatureDateField) {
            signatureDateField.value = today;
        }
        if (declarationDateField) {
            declarationDateField.value = today;
        }

        // Initialize external library integration
        this.initializeLibraryIntegration();
        
        // Conditional field handlers for radio button groups
        
        // Show/hide pets details based on pets radio buttons
        const petsRadios = document.querySelectorAll('input[name="pets_has"]');
        const petsDetailsSection = document.getElementById('pets-details-section');
        
        petsRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const showDetails = document.querySelector('input[name="pets_has"]:checked')?.value === 'true';
                if (petsDetailsSection) {
                    petsDetailsSection.style.display = showDetails ? 'block' : 'none';
                    const petsDetailsField = document.getElementById('pets_details');
                    if (petsDetailsField) {
                        if (showDetails) {
                            petsDetailsField.setAttribute('required', 'required');
                        } else {
                            petsDetailsField.removeAttribute('required');
                            petsDetailsField.value = '';
                        }
                    }
                }
                this.updateSubmitButtonState();
            }.bind(this));
        });
        
        // Show/hide smoking details based on smoking radio buttons
        const smokingRadios = document.querySelectorAll('input[name="smoke"]');
        const smokingDetailsSection = document.getElementById('smoke-details-section');
        
        smokingRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const showDetails = document.querySelector('input[name="smoke"]:checked')?.value === 'true';
                if (smokingDetailsSection) {
                    smokingDetailsSection.style.display = showDetails ? 'block' : 'none';
                    const smokingDetailsField = document.getElementById('smoke_details');
                    if (smokingDetailsField) {
                        if (!showDetails) {
                            smokingDetailsField.value = '';
                        }
                    }
                }
                this.updateSubmitButtonState();
            }.bind(this));
        });
        
        // Show/hide vaping details based on vaping radio buttons
        const vapingRadios = document.querySelectorAll('input[name="vaping"]');
        const vapingDetailsSection = document.getElementById('vaping-details-section');
        
        vapingRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const showDetails = document.querySelector('input[name="vaping"]:checked')?.value === 'true';
                if (vapingDetailsSection) {
                    vapingDetailsSection.style.display = showDetails ? 'block' : 'none';
                    const vapingDetailsField = document.getElementById('vaping_details');
                    if (vapingDetailsField) {
                        if (!showDetails) {
                            vapingDetailsField.value = '';
                        }
                    }
                }
                this.updateSubmitButtonState();
            }.bind(this));
        });
        
        // Show/hide coliving details based on coliving radio buttons
        const colivingRadios = document.querySelectorAll('input[name="coliving_has"]');
        const colivingDetailsSection = document.getElementById('coliving-details-section');
        
        colivingRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const showDetails = document.querySelector('input[name="coliving_has"]:checked')?.value === 'true';
                if (colivingDetailsSection) {
                    colivingDetailsSection.style.display = showDetails ? 'block' : 'none';
                    const colivingDetailsField = document.getElementById('coliving_details');
                    if (colivingDetailsField) {
                        if (showDetails) {
                            colivingDetailsField.setAttribute('required', 'required');
                        } else {
                            colivingDetailsField.removeAttribute('required');
                            colivingDetailsField.value = '';
                        }
                    }
                }
                this.updateSubmitButtonState();
            }.bind(this));
        });
        
        // Show/hide medical condition details based on medical condition radio buttons
        const medicalRadios = document.querySelectorAll('input[name="medical_condition_has"]');
        const medicalDetailsSection = document.getElementById('medical-condition-details-section');
        
        medicalRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const showDetails = document.querySelector('input[name="medical_condition_has"]:checked')?.value === 'true';
                if (medicalDetailsSection) {
                    medicalDetailsSection.style.display = showDetails ? 'block' : 'none';
                    const medicalDetailsField = document.getElementById('medical_condition_details');
                    if (medicalDetailsField) {
                        if (showDetails) {
                            medicalDetailsField.setAttribute('required', 'required');
                        } else {
                            medicalDetailsField.removeAttribute('required');
                            medicalDetailsField.value = '';
                        }
                    }
                }
                this.updateSubmitButtonState();
            }.bind(this));
        });
        
        // Auto-populate signature fields when full name is entered
        const fullNameField = document.getElementById('full_name');
        const signatureField = document.getElementById('signature');
        const printNameField = document.getElementById('print_name');
        const declarationSignatureField = document.getElementById('declaration_signature');
        const declarationPrintNameField = document.getElementById('declaration_print_name');
        
        if (fullNameField) {
            fullNameField.addEventListener('input', function() {
                const name = this.value;
                if (signatureField && !signatureField.value) signatureField.value = name;
                if (printNameField && !printNameField.value) printNameField.value = name;
                if (declarationSignatureField && !declarationSignatureField.value) declarationSignatureField.value = name;
                if (declarationPrintNameField && !declarationPrintNameField.value) declarationPrintNameField.value = name;
            });
        }
        
        // Form submission
        document.getElementById('accommodation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });
        
        // Form validation on change for required fields
        this.addFormValidation();
        
        // Initial submit button state
        setTimeout(() => this.updateSubmitButtonState(), 100);
    }

    async initializeLibraryIntegration() {
        try {
            // Initialize the external library integration system
            if (typeof window.externalLibraryAPI !== 'undefined') {
                await window.externalLibraryAPI.init();
                
                // Create library selector
                await window.externalLibraryAPI.createSelector('library-selector-container', {
                    selectId: 'document-library',
                    placeholder: 'Choose a document library...',
                    allowMultiple: true,
                    showDescriptions: true,
                    onChange: (library, event) => {
                        this.handleLibrarySelection(library, event);
                    }
                });
                
                // Listen for library selection events
                document.addEventListener('librarySelected', (event) => {
                    this.handleLibrarySelectionEvent(event);
                });
                
                console.log('External library integration initialized successfully');
            } else {
                console.warn('External library API not available - library selector will not be functional');
                this.showLibraryLoadError();
            }
        } catch (error) {
            console.error('Failed to initialize library integration:', error);
            this.showLibraryLoadError();
        }
    }

    handleLibrarySelection(library, event) {
        if (library) {
            console.log('Library selected:', library.name);
            this.addSelectedLibrary(library);
        }
    }

    handleLibrarySelectionEvent(event) {
        const library = event.detail.library;
        if (library) {
            console.log('Library selection event:', library.name);
            this.addSelectedLibrary(library);
        }
    }

    addSelectedLibrary(library) {
        const selectedContainer = document.getElementById('selected-libraries');
        const selectedList = document.getElementById('selected-libraries-list');
        
        if (!selectedContainer || !selectedList) return;

        // Check if library is already selected
        const existingCard = selectedList.querySelector(`[data-library-id="${library.id}"]`);
        if (existingCard) {
            this.showAlert(`Library "${library.name}" is already selected.`, 'info');
            return;
        }

        // Create library card
        const libraryCard = document.createElement('div');
        libraryCard.className = 'card mb-2';
        libraryCard.setAttribute('data-library-id', library.id);
        libraryCard.innerHTML = `
            <div class="card-body py-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-1">${this.escapeHtml(library.name)}</h6>
                        ${library.description ? `<small class="text-muted">${this.escapeHtml(library.description)}</small>` : ''}
                    </div>
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="accommodationForm.removeSelectedLibrary('${library.id}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;

        selectedList.appendChild(libraryCard);
        selectedContainer.style.display = 'block';

        // Store library data for form submission
        if (!this.formData.selected_libraries) {
            this.formData.selected_libraries = [];
        }
        this.formData.selected_libraries.push({
            id: library.id,
            name: library.name,
            url: library.url,
            description: library.description
        });
    }

    removeSelectedLibrary(libraryId) {
        const libraryCard = document.querySelector(`[data-library-id="${libraryId}"]`);
        if (libraryCard) {
            libraryCard.remove();
        }

        // Remove from form data
        if (this.formData.selected_libraries) {
            this.formData.selected_libraries = this.formData.selected_libraries.filter(
                lib => lib.id !== libraryId
            );
        }

        // Hide container if no libraries selected
        const selectedList = document.getElementById('selected-libraries-list');
        const selectedContainer = document.getElementById('selected-libraries');
        if (selectedList && selectedList.children.length === 0 && selectedContainer) {
            selectedContainer.style.display = 'none';
        }
    }

    showLibraryLoadError() {
        const container = document.getElementById('library-selector-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    External library system is not available. You can still submit the form, but library selection is disabled.
                </div>
            `;
        }
    }
    
    addFormValidation() {
        // Add real-time validation for required fields
        const requiredFields = document.querySelectorAll('input[required], select[required], textarea[required]');
        
        requiredFields.forEach(field => {
            field.addEventListener('blur', function() {
                this.validateField(field);
            }.bind(this));
            
            field.addEventListener('input', function() {
                this.validateField(field);
            }.bind(this));
            
            field.addEventListener('change', function() {
                this.validateField(field);
            }.bind(this));
        });
    }
    
    validateField(field) {
        let isValid = field.checkValidity();
        let customErrorMessage = '';
        
        // Custom validation for specific fields with user-friendly messages
        if (field.id === 'ni_number' && field.value.trim()) {
            isValid = this.validateNationalInsuranceNumber(field.value.trim());
            if (!isValid) {
                customErrorMessage = 'Please check your National Insurance number format (example: AB123456C)';
            }
        }
        
        if (field.type === 'email' && field.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value.trim())) {
                isValid = false;
                customErrorMessage = 'Please enter a valid email address like example@email.com';
            }
        }
        
        if (field.type === 'tel' && field.value.trim()) {
            const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
            if (!phoneRegex.test(field.value.trim())) {
                isValid = false;
                customErrorMessage = 'Please enter a valid phone number with at least 10 digits';
            }
        }
        
        // Required field validation with user-friendly message
        if (!field.value.trim() && field.required) {
            isValid = false;
            customErrorMessage = 'This information is required';
        }
        
        // Apply validation styling
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            this.clearFieldError(field);
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            this.setFieldError(field, customErrorMessage);
        }
        
        // Update section highlighting
        this.updateSectionValidation(field);
        
        // Update submit button state
        this.updateSubmitButtonState();
        
        return isValid;
    }
    
    updateSectionValidation(field) {
        // Find the form section containing this field
        const formSection = field.closest('.form-section');
        if (!formSection) return;
        
        // Check if any fields in this section have validation errors
        const invalidFields = formSection.querySelectorAll('.is-invalid');
        
        if (invalidFields.length > 0) {
            formSection.classList.add('has-error');
        } else {
            formSection.classList.remove('has-error');
        }
    }
    
    validateNationalInsuranceNumber(niNumber) {
        // UK National Insurance number format: 2 letters, 6 digits, 1 letter
        // Pattern: AB123456C
        const niRegex = /^[A-CEGHJ-PR-TW-Z]{1}[A-CEGHJ-NPR-TW-Z]{1}[0-9]{6}[A-D]{1}$/i;
        
        if (!niRegex.test(niNumber)) {
            return false;
        }
        
        // Additional validation: certain letter combinations are not allowed
        const invalidPrefixes = ['BG', 'GB', 'NK', 'KN', 'TN', 'NT', 'ZZ'];
        const prefix = niNumber.substring(0, 2).toUpperCase();
        
        if (invalidPrefixes.includes(prefix)) {
            return false;
        }
        
        return true;
    }
    
    setFieldError(field, message) {
        if (!message) return;
        
        // Remove existing error message
        this.clearFieldError(field);
        
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        errorDiv.setAttribute('data-field-error', field.id);
        
        // Insert after the field
        field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }
    
    clearFieldError(field) {
        const errorElement = field.parentNode.querySelector(`[data-field-error="${field.id}"]`);
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    validateForm() {
        let isValid = true;
        const errors = [];
        const requiredFields = document.querySelectorAll('input[required], select[required], textarea[required]');
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
                const label = this.getFieldLabel(field);
                errors.push({
                    field: field,
                    label: label,
                    message: this.getFieldErrorMessage(field)
                });
            }
        });
        
        // Show error summary if there are errors
        if (!isValid) {
            this.showErrorSummary(errors);
        } else {
            this.hideErrorSummary();
        }
        
        return isValid;
    }
    
    getFieldLabel(field) {
        const label = document.querySelector(`label[for="${field.id}"]`);
        if (label) {
            return label.textContent.replace('*', '').trim();
        }
        return field.name || field.id || 'Field';
    }
    
    getFieldErrorMessage(field) {
        if (!field.value.trim() && field.required) {
            return 'This information is required';
        }
        
        if (field.id === 'ni_number' && field.value.trim()) {
            return 'Please check your National Insurance number format';
        }
        
        if (field.type === 'email' && field.value.trim()) {
            return 'Please enter a valid email address like example@email.com';
        }
        
        if (field.type === 'tel' && field.value.trim()) {
            return 'Please enter a valid phone number with at least 10 digits';
        }
        
        return 'Please check this information';
    }
    
    showErrorSummary(errors) {
        // Create or update error summary
        let errorSummary = document.getElementById('validation-error-summary');
        
        if (!errorSummary) {
            errorSummary = document.createElement('div');
            errorSummary.id = 'validation-error-summary';
            errorSummary.className = 'alert alert-danger';
            errorSummary.setAttribute('role', 'alert');
            
            // Insert before submit button
            const submitSection = document.querySelector('.form-section:last-child');
            if (submitSection) {
                submitSection.parentNode.insertBefore(errorSummary, submitSection);
            }
        }
        
        // Build error summary content
        let summaryHTML = `
            <h5><i class="fas fa-exclamation-triangle me-2"></i>Please fix the following errors:</h5>
            <ul class="mb-0">
        `;
        
        errors.forEach(error => {
            summaryHTML += `<li><a href="#${error.field.id}" class="alert-link">${error.label}: ${error.message}</a></li>`;
        });
        
        summaryHTML += '</ul>';
        errorSummary.innerHTML = summaryHTML;
        
        // Add click handlers to error links
        errorSummary.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetField = document.getElementById(targetId);
                if (targetField) {
                    targetField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    targetField.focus();
                }
            });
        });
        
        // Scroll to error summary
        errorSummary.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    hideErrorSummary() {
        const errorSummary = document.getElementById('validation-error-summary');
        if (errorSummary) {
            errorSummary.remove();
        }
    }
    
    updateSubmitButtonState() {
        const submitButton = document.querySelector('button[type="submit"]');
        if (!submitButton) return;
        
        const requiredFields = document.querySelectorAll('input[required], select[required], textarea[required]');
        let allValid = true;
        
        for (const field of requiredFields) {
            if (!field.value.trim() || field.classList.contains('is-invalid')) {
                allValid = false;
                break;
            }
        }
        
        if (allValid) {
            submitButton.disabled = false;
            submitButton.classList.remove('btn-secondary');
            submitButton.classList.add('btn-primary');
        } else {
            submitButton.disabled = true;
            submitButton.classList.remove('btn-primary');
            submitButton.classList.add('btn-secondary');
        }
    }

    
    async submitForm() {
        try {
            // Validate form first
            if (!this.validateForm()) {
                this.showAlert('Please fill in all required fields correctly before submitting.', 'danger');
                return;
            }
            
            this.showLoading('Submitting application...');
            this.updateStep(4);
            
            // Collect form data
            const formData = this.collectFormData();
            
            // Create the proper FormSubmissionRequest structure
            const submissionRequest = {
                form_data: formData,
                email_verification_token: this.sessionToken,
                math_question: this.mathQuestion || "2 + 2",
                math_answer: 4
            };
            
            // Submit to server
            const response = await fetch('/api/form/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-Token': this.sessionToken
                },
                body: JSON.stringify(submissionRequest)
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
        // Collect comprehensive form data from all visible form fields
        return {
            tenant_details: {
                full_name: document.getElementById('full_name')?.value || '',
                date_of_birth: document.getElementById('date_of_birth')?.value || '',
                place_of_birth: document.getElementById('place_of_birth')?.value || '',
                email: document.getElementById('email_readonly')?.value || document.getElementById('email')?.value || '',
                telephone: document.getElementById('telephone')?.value || '',
                gender: document.getElementById('gender')?.value || '',
                ni_number: document.getElementById('ni_number')?.value || '',
                car: document.getElementById('car')?.checked || false,
                bicycle: document.getElementById('bicycle')?.checked || false,
                right_to_live_in_uk: document.querySelector('input[name="right_to_live_in_uk"]:checked')?.value === 'true' || false,
                room_occupancy: document.getElementById('room_occupancy')?.value || '',
                other_names_has: false, // Not implemented in current form
                other_names_details: null,
                medical_condition_has: document.querySelector('input[name="medical_condition_has"]:checked')?.value === 'true' || false,
                medical_condition_details: document.getElementById('medical_condition_details')?.value || null
            },
            bank_details: {
                bank_name: document.getElementById('bank_name')?.value || '',
                bank_branch_address: document.getElementById('bank_branch_address')?.value || '',
                account_no: document.getElementById('account_no')?.value || '',
                sort_code: document.getElementById('sort_code')?.value || ''
            },
            address_history: [
                // Current address (0)
                {
                    address: document.getElementById('address_0')?.value || '',
                    from_date: document.getElementById('from_date_0')?.value || '',
                    to_date: null, // Current address
                    landlord_name: document.getElementById('landlord_name_0')?.value || '',
                    landlord_tel: document.getElementById('landlord_tel_0')?.value || '',
                    landlord_email: document.getElementById('landlord_email_0')?.value || '',
                    reason_for_leaving: document.getElementById('reason_leaving_0')?.value || null
                },
                // Previous address 1 (if filled)
                ...(document.getElementById('address_1')?.value ? [{
                    address: document.getElementById('address_1')?.value || '',
                    from_date: document.getElementById('from_date_1')?.value || '',
                    to_date: document.getElementById('to_date_1')?.value || '',
                    landlord_name: document.getElementById('landlord_name_1')?.value || '',
                    landlord_tel: document.getElementById('landlord_tel_1')?.value || '',
                    landlord_email: document.getElementById('landlord_email_1')?.value || '',
                    reason_for_leaving: document.getElementById('reason_leaving_1')?.value || null
                }] : []),
                // Previous address 2 (if filled)
                ...(document.getElementById('address_2')?.value ? [{
                    address: document.getElementById('address_2')?.value || '',
                    from_date: document.getElementById('from_date_2')?.value || '',
                    to_date: document.getElementById('to_date_2')?.value || '',
                    landlord_name: document.getElementById('landlord_name_2')?.value || '',
                    landlord_tel: document.getElementById('landlord_tel_2')?.value || '',
                    landlord_email: document.getElementById('landlord_email_2')?.value || '',
                    reason_for_leaving: document.getElementById('reason_leaving_2')?.value || null
                }] : [])
            ],
            contacts: {
                next_of_kin: document.getElementById('next_of_kin')?.value || '',
                relationship: document.getElementById('relationship')?.value || '',
                address: document.getElementById('contact_address')?.value || '',
                contact_number: document.getElementById('contact_number')?.value || ''
            },
            medical_details: {
                gp_practice: document.getElementById('gp_practice')?.value || '',
                doctor_name: document.getElementById('doctor_name')?.value || '',
                doctor_address: document.getElementById('doctor_address')?.value || '',
                doctor_telephone: document.getElementById('doctor_telephone')?.value || ''
            },
            employment: {
                employer_name_address: document.getElementById('employer_name_address')?.value || '',
                employers_name: document.getElementById('employers_name')?.value || '',
                job_title: document.getElementById('job_title')?.value || '',
                manager_name: document.getElementById('manager_name')?.value || '',
                manager_tel: document.getElementById('manager_tel')?.value || '',
                manager_email: document.getElementById('manager_email')?.value || '',
                date_of_employment: document.getElementById('date_of_employment')?.value || '',
                present_salary: parseFloat(document.getElementById('present_salary')?.value) || 0
            },
            employment_change: document.getElementById('employment_change')?.value || null,
            passport_details: {
                passport_number: document.getElementById('passport_number')?.value || '',
                date_of_issue: document.getElementById('passport_date_of_issue')?.value || '',
                place_of_issue: document.getElementById('passport_place_of_issue')?.value || ''
            },
            other_details: {
                pets_has: document.querySelector('input[name="pets_has"]:checked')?.value === 'true' || false,
                pets_details: document.getElementById('pets_details')?.value || null,
                smoke: document.querySelector('input[name="smoke"]:checked')?.value === 'true' || false,
                smoke_details: document.getElementById('smoke_details')?.value || null,
                vaping: document.querySelector('input[name="vaping"]:checked')?.value === 'true' || false,
                vaping_details: document.getElementById('vaping_details')?.value || null,
                coliving_has: document.querySelector('input[name="coliving_has"]:checked')?.value === 'true' || false,
                coliving_details: document.getElementById('coliving_details')?.value || null
            },
            occupation_agreement: {
                single_occupancy_agree: document.querySelector('input[name="single_occupancy_agree"]:checked')?.value === 'true' || false,
                hmo_terms_agree: document.querySelector('input[name="hmo_terms_agree"]:checked')?.value === 'true' || false,
                no_unlisted_occupants: document.querySelector('input[name="no_unlisted_occupants"]:checked')?.value === 'true' || false,
                no_smoking: document.querySelector('input[name="no_smoking_agree"]:checked')?.value === 'true' || false,
                kitchen_cooking_only: document.querySelector('input[name="kitchen_cooking_only"]:checked')?.value === 'true' || false
            },
            consent_and_declaration: {
                consent_given: document.getElementById('consent_given')?.checked || false,
                signature: document.getElementById('signature')?.value || '',
                date: document.getElementById('signature_date')?.value || '',
                print_name: document.getElementById('print_name')?.value || '',
                declaration: {
                    main_home: document.getElementById('main_home')?.checked || false,
                    enquiries_permission: document.getElementById('enquiries_permission')?.checked || false,
                    certify_no_judgements: document.getElementById('certify_no_judgements')?.checked || false,
                    certify_no_housing_debt: document.getElementById('certify_no_housing_debt')?.checked || false,
                    certify_no_landlord_debt: document.getElementById('certify_no_landlord_debt')?.checked || false,
                    certify_no_abuse: document.getElementById('certify_no_abuse')?.checked || false,
                    certify_no_alcohol_substance_abuse: document.getElementById('certify_no_alcohol_substance_abuse')?.checked || false
                },
                declaration_signature: document.getElementById('declaration_signature')?.value || '',
                declaration_date: document.getElementById('declaration_date')?.value || '',
                declaration_print_name: document.getElementById('declaration_print_name')?.value || ''
            },
            selected_libraries: this.formData.selected_libraries || [],
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

    // Utility method for HTML escaping
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.accommodationForm = new AzureAccommodationForm();
});
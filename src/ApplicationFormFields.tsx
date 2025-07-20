import React, { useState } from 'react'

// TypeScript types based on form_schema.json
interface TenantDetails {
  full_name: string
  date_of_birth: string
  place_of_birth: string
  email: string
  telephone: string
  employers_name: string
  gender: 'male' | 'female' | ''
  ni_number: string
  car: boolean
  bicycle: boolean
  right_to_live_in_uk: boolean
  other_names: {
    has_other_names: boolean
    details: string
  }
  room_occupancy: 'just_you' | 'you_and_someone_else' | ''
  medical_condition: {
    has_condition: boolean
    details: string
  }
}

interface BankDetails {
  bank_name: string
  postcode: string
  account_no: string
  sort_code: string
}

interface AddressHistoryItem {
  address: string
  from: string
  to: string
  landlord_name: string
  landlord_tel: string
  landlord_email: string
}

interface Contacts {
  next_of_kin: string
  relationship: string
  address: string
  contact_number: string
}

interface MedicalDetails {
  gp_practice: string
  doctor_name: string
  doctor_address: string
  doctor_telephone: string
}

interface Employment {
  employer_name: string
  employer_address: string
  job_title: string
  manager_name: string
  manager_tel: string
  manager_email: string
  date_of_employment: string
  present_salary: string
}

interface PassportDetails {
  passport_number: string
  date_of_issue: string
  place_of_issue: string
}

interface CurrentLivingArrangement {
  landlord_knows: boolean
  notice_end_date: string
  reason_leaving: string
  landlord_reference: boolean
  landlord_contact: {
    name: string
    address: string
    tel: string
    email: string
  }
}

interface Other {
  pets: {
    has_pets: boolean
    details: string
  }
  smoke: boolean
  coliving: {
    has_coliving: boolean
    details: string
  }
}

interface OccupationAgreement {
  single_occupancy_agree: boolean
  hmo_terms_agree: boolean
  no_unlisted_occupants: boolean
  no_smoking: boolean
  kitchen_cooking_only: boolean
}

interface ConsentAndDeclaration {
  consent_given: boolean
  signature: string
  date: string
  print_name: string
  declaration: {
    main_home: boolean
    enquiries_permission: boolean
    certify_no_judgements: boolean
    certify_no_housing_debt: boolean
    certify_no_landlord_debt: boolean
    certify_no_abuse: boolean
  }
  declaration_signature: string
  declaration_date: string
  declaration_print_name: string
}

interface FormData {
  tenant_details: TenantDetails
  bank_details: BankDetails
  address_history: AddressHistoryItem[]
  contacts: Contacts
  medical_details: MedicalDetails
  employment: Employment
  employment_change: string
  passport_details: PassportDetails
  current_living_arrangement: CurrentLivingArrangement
  other: Other
  occupation_agreement: OccupationAgreement
  consent_and_declaration: ConsentAndDeclaration
}

const ApplicationFormFields: React.FC = () => {
  // Initialize form data with empty values
  const [formData, setFormData] = useState<FormData>({
    tenant_details: {
      full_name: '',
      date_of_birth: '',
      place_of_birth: '',
      email: '',
      telephone: '',
      employers_name: '',
      gender: '',
      ni_number: '',
      car: false,
      bicycle: false,
      right_to_live_in_uk: false,
      other_names: {
        has_other_names: false,
        details: ''
      },
      room_occupancy: '',
      medical_condition: {
        has_condition: false,
        details: ''
      }
    },
    bank_details: {
      bank_name: '',
      postcode: '',
      account_no: '',
      sort_code: ''
    },
    address_history: [{
      address: '',
      from: '',
      to: '',
      landlord_name: '',
      landlord_tel: '',
      landlord_email: ''
    }],
    contacts: {
      next_of_kin: '',
      relationship: '',
      address: '',
      contact_number: ''
    },
    medical_details: {
      gp_practice: '',
      doctor_name: '',
      doctor_address: '',
      doctor_telephone: ''
    },
    employment: {
      employer_name: '',
      employer_address: '',
      job_title: '',
      manager_name: '',
      manager_tel: '',
      manager_email: '',
      date_of_employment: '',
      present_salary: ''
    },
    employment_change: '',
    passport_details: {
      passport_number: '',
      date_of_issue: '',
      place_of_issue: ''
    },
    current_living_arrangement: {
      landlord_knows: false,
      notice_end_date: '',
      reason_leaving: '',
      landlord_reference: false,
      landlord_contact: {
        name: '',
        address: '',
        tel: '',
        email: ''
      }
    },
    other: {
      pets: {
        has_pets: false,
        details: ''
      },
      smoke: false,
      coliving: {
        has_coliving: false,
        details: ''
      }
    },
    occupation_agreement: {
      single_occupancy_agree: false,
      hmo_terms_agree: false,
      no_unlisted_occupants: false,
      no_smoking: false,
      kitchen_cooking_only: false
    },
    consent_and_declaration: {
      consent_given: false,
      signature: '',
      date: '',
      print_name: '',
      declaration: {
        main_home: false,
        enquiries_permission: false,
        certify_no_judgements: false,
        certify_no_housing_debt: false,
        certify_no_landlord_debt: false,
        certify_no_abuse: false
      },
      declaration_signature: '',
      declaration_date: '',
      declaration_print_name: ''
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Form Data Submitted:', formData)
    alert('Form submitted successfully! Check the console for form data.')
  }

  // Helper function to update nested form data
  const updateFormData = (section: keyof FormData, field: string, value: any) => {
    setFormData(prev => {
      const sectionData = prev[section] as Record<string, any>
      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: value
        }
      }
    })
  }

  // Helper function to update deeply nested form data
  const updateNestedFormData = (section: keyof FormData, nestedField: string, field: string, value: any) => {
    setFormData(prev => {
      const sectionData = prev[section] as Record<string, any>
      const nestedData = sectionData[nestedField] as Record<string, any>
      return {
        ...prev,
        [section]: {
          ...sectionData,
          [nestedField]: {
            ...nestedData,
            [field]: value
          }
        }
      }
    })
  }

  const addAddressHistoryItem = () => {
    setFormData(prev => ({
      ...prev,
      address_history: [
        ...prev.address_history,
        {
          address: '',
          from: '',
          to: '',
          landlord_name: '',
          landlord_tel: '',
          landlord_email: ''
        }
      ]
    }))
  }

  const updateAddressHistoryItem = (index: number, field: keyof AddressHistoryItem, value: string) => {
    setFormData(prev => ({
      ...prev,
      address_history: prev.address_history.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }))
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Tenant Details Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>1. Tenant Details</strong></legend>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label htmlFor="full_name">Full Name *</label>
            <input
              type="text"
              id="full_name"
              required
              value={formData.tenant_details.full_name}
              onChange={(e) => updateFormData('tenant_details', 'full_name', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="date_of_birth">Date of Birth *</label>
            <input
              type="date"
              id="date_of_birth"
              required
              value={formData.tenant_details.date_of_birth}
              onChange={(e) => updateFormData('tenant_details', 'date_of_birth', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="place_of_birth">Place of Birth</label>
            <input
              type="text"
              id="place_of_birth"
              value={formData.tenant_details.place_of_birth}
              onChange={(e) => updateFormData('tenant_details', 'place_of_birth', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              required
              value={formData.tenant_details.email}
              onChange={(e) => updateFormData('tenant_details', 'email', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="telephone">Telephone *</label>
            <input
              type="tel"
              id="telephone"
              required
              value={formData.tenant_details.telephone}
              onChange={(e) => updateFormData('tenant_details', 'telephone', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="employers_name">Employer's Name</label>
            <input
              type="text"
              id="employers_name"
              value={formData.tenant_details.employers_name}
              onChange={(e) => updateFormData('tenant_details', 'employers_name', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="gender">Gender</label>
            <select
              id="gender"
              value={formData.tenant_details.gender}
              onChange={(e) => updateFormData('tenant_details', 'gender', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            >
              <option value="">Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="ni_number">NI Number</label>
            <input
              type="text"
              id="ni_number"
              value={formData.tenant_details.ni_number}
              onChange={(e) => updateFormData('tenant_details', 'ni_number', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="room_occupancy">Room Occupancy</label>
            <select
              id="room_occupancy"
              value={formData.tenant_details.room_occupancy}
              onChange={(e) => updateFormData('tenant_details', 'room_occupancy', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            >
              <option value="">Select Occupancy</option>
              <option value="just_you">Just You</option>
              <option value="you_and_someone_else">You and Someone Else</option>
            </select>
          </div>
        </div>
        
        <div style={{ marginTop: '10px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.tenant_details.car}
              onChange={(e) => updateFormData('tenant_details', 'car', e.target.checked)}
            />
            Do you have a car?
          </label>
        </div>
        
        <div>
          <label>
            <input
              type="checkbox"
              checked={formData.tenant_details.bicycle}
              onChange={(e) => updateFormData('tenant_details', 'bicycle', e.target.checked)}
            />
            Do you have a bicycle?
          </label>
        </div>
        
        <div>
          <label>
            <input
              type="checkbox"
              checked={formData.tenant_details.right_to_live_in_uk}
              onChange={(e) => updateFormData('tenant_details', 'right_to_live_in_uk', e.target.checked)}
            />
            Do you have the right to live in the UK?
          </label>
        </div>
        
        <div style={{ marginTop: '10px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.tenant_details.other_names.has_other_names}
              onChange={(e) => updateNestedFormData('tenant_details', 'other_names', 'has_other_names', e.target.checked)}
            />
            Have you been known by any other name?
          </label>
          {formData.tenant_details.other_names.has_other_names && (
            <input
              type="text"
              placeholder="Please specify"
              value={formData.tenant_details.other_names.details}
              onChange={(e) => updateNestedFormData('tenant_details', 'other_names', 'details', e.target.value)}
              style={{ width: '100%', padding: '5px', marginTop: '5px' }}
            />
          )}
        </div>
        
        <div style={{ marginTop: '10px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.tenant_details.medical_condition.has_condition}
              onChange={(e) => updateNestedFormData('tenant_details', 'medical_condition', 'has_condition', e.target.checked)}
            />
            Medical condition other residents need to know?
          </label>
          {formData.tenant_details.medical_condition.has_condition && (
            <textarea
              placeholder="Please specify"
              value={formData.tenant_details.medical_condition.details}
              onChange={(e) => updateNestedFormData('tenant_details', 'medical_condition', 'details', e.target.value)}
              style={{ width: '100%', padding: '5px', marginTop: '5px' }}
              rows={3}
            />
          )}
        </div>
      </fieldset>

      {/* Bank Details Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>2. Bank Details</strong></legend>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label htmlFor="bank_name">Name of Bank</label>
            <input
              type="text"
              id="bank_name"
              value={formData.bank_details.bank_name}
              onChange={(e) => updateFormData('bank_details', 'bank_name', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="bank_postcode">Postcode</label>
            <input
              type="text"
              id="bank_postcode"
              value={formData.bank_details.postcode}
              onChange={(e) => updateFormData('bank_details', 'postcode', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="account_no">Account No</label>
            <input
              type="text"
              id="account_no"
              value={formData.bank_details.account_no}
              onChange={(e) => updateFormData('bank_details', 'account_no', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="sort_code">Sort Code</label>
            <input
              type="text"
              id="sort_code"
              value={formData.bank_details.sort_code}
              onChange={(e) => updateFormData('bank_details', 'sort_code', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
        </div>
      </fieldset>

      {/* Address History Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>3. Address History (3 years)</strong></legend>
        
        {formData.address_history.map((address, index) => (
          <div key={index} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #eee', borderRadius: '3px' }}>
            <h4>Address {index + 1}</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div style={{ gridColumn: '1 / -1' }}>
                <label htmlFor={`address_${index}`}>Address</label>
                <textarea
                  id={`address_${index}`}
                  value={address.address}
                  onChange={(e) => updateAddressHistoryItem(index, 'address', e.target.value)}
                  style={{ width: '100%', padding: '5px' }}
                  rows={2}
                />
              </div>
              
              <div>
                <label htmlFor={`from_${index}`}>From</label>
                <input
                  type="date"
                  id={`from_${index}`}
                  value={address.from}
                  onChange={(e) => updateAddressHistoryItem(index, 'from', e.target.value)}
                  style={{ width: '100%', padding: '5px' }}
                />
              </div>
              
              <div>
                <label htmlFor={`to_${index}`}>To</label>
                <input
                  type="date"
                  id={`to_${index}`}
                  value={address.to}
                  onChange={(e) => updateAddressHistoryItem(index, 'to', e.target.value)}
                  style={{ width: '100%', padding: '5px' }}
                />
              </div>
              
              <div>
                <label htmlFor={`landlord_name_${index}`}>Landlord/Agent Name</label>
                <input
                  type="text"
                  id={`landlord_name_${index}`}
                  value={address.landlord_name}
                  onChange={(e) => updateAddressHistoryItem(index, 'landlord_name', e.target.value)}
                  style={{ width: '100%', padding: '5px' }}
                />
              </div>
              
              <div>
                <label htmlFor={`landlord_tel_${index}`}>Landlord Tel</label>
                <input
                  type="tel"
                  id={`landlord_tel_${index}`}
                  value={address.landlord_tel}
                  onChange={(e) => updateAddressHistoryItem(index, 'landlord_tel', e.target.value)}
                  style={{ width: '100%', padding: '5px' }}
                />
              </div>
              
              <div style={{ gridColumn: '1 / -1' }}>
                <label htmlFor={`landlord_email_${index}`}>Landlord Email</label>
                <input
                  type="email"
                  id={`landlord_email_${index}`}
                  value={address.landlord_email}
                  onChange={(e) => updateAddressHistoryItem(index, 'landlord_email', e.target.value)}
                  style={{ width: '100%', padding: '5px' }}
                />
              </div>
            </div>
          </div>
        ))}
        
        <button type="button" onClick={addAddressHistoryItem} style={{ padding: '8px 16px', backgroundColor: '#007acc', color: 'white', border: 'none', borderRadius: '3px' }}>
          Add Another Address
        </button>
      </fieldset>

      {/* Contacts Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>4. Contacts</strong></legend>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label htmlFor="next_of_kin">Next of Kin</label>
            <input
              type="text"
              id="next_of_kin"
              value={formData.contacts.next_of_kin}
              onChange={(e) => updateFormData('contacts', 'next_of_kin', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="relationship">Relationship</label>
            <input
              type="text"
              id="relationship"
              value={formData.contacts.relationship}
              onChange={(e) => updateFormData('contacts', 'relationship', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="contact_address">Address</label>
            <textarea
              id="contact_address"
              value={formData.contacts.address}
              onChange={(e) => updateFormData('contacts', 'address', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
              rows={2}
            />
          </div>
          
          <div>
            <label htmlFor="contact_number">Contact Number</label>
            <input
              type="tel"
              id="contact_number"
              value={formData.contacts.contact_number}
              onChange={(e) => updateFormData('contacts', 'contact_number', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
        </div>
      </fieldset>

      {/* Medical Details Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>5. Medical Details</strong></legend>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label htmlFor="gp_practice">GP Practice</label>
            <input
              type="text"
              id="gp_practice"
              value={formData.medical_details.gp_practice}
              onChange={(e) => updateFormData('medical_details', 'gp_practice', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="doctor_name">Doctor's Name</label>
            <input
              type="text"
              id="doctor_name"
              value={formData.medical_details.doctor_name}
              onChange={(e) => updateFormData('medical_details', 'doctor_name', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="doctor_address">Doctor's Address</label>
            <textarea
              id="doctor_address"
              value={formData.medical_details.doctor_address}
              onChange={(e) => updateFormData('medical_details', 'doctor_address', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
              rows={2}
            />
          </div>
          
          <div>
            <label htmlFor="doctor_telephone">Doctor's Telephone No</label>
            <input
              type="tel"
              id="doctor_telephone"
              value={formData.medical_details.doctor_telephone}
              onChange={(e) => updateFormData('medical_details', 'doctor_telephone', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
        </div>
      </fieldset>

      {/* Employment Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>6. Employment</strong></legend>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label htmlFor="employer_name">Name & Address of Employer</label>
            <textarea
              id="employer_name"
              value={formData.employment.employer_name}
              onChange={(e) => updateFormData('employment', 'employer_name', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
              rows={2}
            />
          </div>
          
          <div>
            <label htmlFor="job_title">Job Title</label>
            <input
              type="text"
              id="job_title"
              value={formData.employment.job_title}
              onChange={(e) => updateFormData('employment', 'job_title', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="manager_name">Manager's Name</label>
            <input
              type="text"
              id="manager_name"
              value={formData.employment.manager_name}
              onChange={(e) => updateFormData('employment', 'manager_name', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="manager_tel">Manager's Tel</label>
            <input
              type="tel"
              id="manager_tel"
              value={formData.employment.manager_tel}
              onChange={(e) => updateFormData('employment', 'manager_tel', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="manager_email">Manager's Email</label>
            <input
              type="email"
              id="manager_email"
              value={formData.employment.manager_email}
              onChange={(e) => updateFormData('employment', 'manager_email', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="date_of_employment">Date of Employment</label>
            <input
              type="date"
              id="date_of_employment"
              value={formData.employment.date_of_employment}
              onChange={(e) => updateFormData('employment', 'date_of_employment', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="present_salary">Present Salary</label>
            <input
              type="text"
              id="present_salary"
              value={formData.employment.present_salary}
              onChange={(e) => updateFormData('employment', 'present_salary', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
        </div>
      </fieldset>

      {/* Employment Change Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>7. Employment Change</strong></legend>
        
        <div>
          <label htmlFor="employment_change">Are circumstances likely to change?</label>
          <textarea
            id="employment_change"
            value={formData.employment_change}
            onChange={(e) => setFormData(prev => ({ ...prev, employment_change: e.target.value }))}
            style={{ width: '100%', padding: '5px' }}
            rows={3}
          />
        </div>
      </fieldset>

      {/* Passport Details Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>8. Passport Details</strong></legend>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label htmlFor="passport_number">Passport Number</label>
            <input
              type="text"
              id="passport_number"
              value={formData.passport_details.passport_number}
              onChange={(e) => updateFormData('passport_details', 'passport_number', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="date_of_issue">Date of Issue</label>
            <input
              type="date"
              id="date_of_issue"
              value={formData.passport_details.date_of_issue}
              onChange={(e) => updateFormData('passport_details', 'date_of_issue', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="place_of_issue">Place of Issue</label>
            <input
              type="text"
              id="place_of_issue"
              value={formData.passport_details.place_of_issue}
              onChange={(e) => updateFormData('passport_details', 'place_of_issue', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
        </div>
      </fieldset>

      {/* Current Living Arrangement Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>9. Current Living Arrangement</strong></legend>
        
        <div style={{ marginBottom: '10px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.current_living_arrangement.landlord_knows}
              onChange={(e) => updateFormData('current_living_arrangement', 'landlord_knows', e.target.checked)}
            />
            Does landlord know you are leaving?
          </label>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
          <div>
            <label htmlFor="notice_end_date">Notice Run Out Date</label>
            <input
              type="date"
              id="notice_end_date"
              value={formData.current_living_arrangement.notice_end_date}
              onChange={(e) => updateFormData('current_living_arrangement', 'notice_end_date', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="reason_leaving">Reason for Leaving</label>
            <input
              type="text"
              id="reason_leaving"
              value={formData.current_living_arrangement.reason_leaving}
              onChange={(e) => updateFormData('current_living_arrangement', 'reason_leaving', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
        </div>
        
        <div style={{ marginBottom: '10px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.current_living_arrangement.landlord_reference}
              onChange={(e) => updateFormData('current_living_arrangement', 'landlord_reference', e.target.checked)}
            />
            Will landlord give reference?
          </label>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <label htmlFor="landlord_contact_name">Existing Landlord/Agent Name</label>
            <input
              type="text"
              id="landlord_contact_name"
              value={formData.current_living_arrangement.landlord_contact.name}
              onChange={(e) => updateNestedFormData('current_living_arrangement', 'landlord_contact', 'name', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="landlord_contact_tel">Contact Tel</label>
            <input
              type="tel"
              id="landlord_contact_tel"
              value={formData.current_living_arrangement.landlord_contact.tel}
              onChange={(e) => updateNestedFormData('current_living_arrangement', 'landlord_contact', 'tel', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
          
          <div>
            <label htmlFor="landlord_contact_address">Contact Address</label>
            <textarea
              id="landlord_contact_address"
              value={formData.current_living_arrangement.landlord_contact.address}
              onChange={(e) => updateNestedFormData('current_living_arrangement', 'landlord_contact', 'address', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
              rows={2}
            />
          </div>
          
          <div>
            <label htmlFor="landlord_contact_email">Contact Email</label>
            <input
              type="email"
              id="landlord_contact_email"
              value={formData.current_living_arrangement.landlord_contact.email}
              onChange={(e) => updateNestedFormData('current_living_arrangement', 'landlord_contact', 'email', e.target.value)}
              style={{ width: '100%', padding: '5px' }}
            />
          </div>
        </div>
      </fieldset>

      {/* Other Details Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>10. Other</strong></legend>
        
        <div style={{ marginBottom: '10px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.other.pets.has_pets}
              onChange={(e) => updateNestedFormData('other', 'pets', 'has_pets', e.target.checked)}
            />
            Do you have pets?
          </label>
          {formData.other.pets.has_pets && (
            <textarea
              placeholder="Please provide details"
              value={formData.other.pets.details}
              onChange={(e) => updateNestedFormData('other', 'pets', 'details', e.target.value)}
              style={{ width: '100%', padding: '5px', marginTop: '5px' }}
              rows={2}
            />
          )}
        </div>
        
        <div style={{ marginBottom: '10px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.other.smoke}
              onChange={(e) => updateFormData('other', 'smoke', e.target.checked)}
            />
            Do you smoke?
          </label>
        </div>
        
        <div>
          <label>
            <input
              type="checkbox"
              checked={formData.other.coliving.has_coliving}
              onChange={(e) => updateNestedFormData('other', 'coliving', 'has_coliving', e.target.checked)}
            />
            Co-living preferences?
          </label>
          {formData.other.coliving.has_coliving && (
            <textarea
              placeholder="Please provide details"
              value={formData.other.coliving.details}
              onChange={(e) => updateNestedFormData('other', 'coliving', 'details', e.target.value)}
              style={{ width: '100%', padding: '5px', marginTop: '5px' }}
              rows={2}
            />
          )}
        </div>
      </fieldset>

      {/* Occupation Agreement Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>11. Occupation Agreement</strong></legend>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label>
            <input
              type="checkbox"
              checked={formData.occupation_agreement.single_occupancy_agree}
              onChange={(e) => updateFormData('occupation_agreement', 'single_occupancy_agree', e.target.checked)}
            />
            I agree to single occupancy terms
          </label>
          
          <label>
            <input
              type="checkbox"
              checked={formData.occupation_agreement.hmo_terms_agree}
              onChange={(e) => updateFormData('occupation_agreement', 'hmo_terms_agree', e.target.checked)}
            />
            I agree to HMO terms and conditions
          </label>
          
          <label>
            <input
              type="checkbox"
              checked={formData.occupation_agreement.no_unlisted_occupants}
              onChange={(e) => updateFormData('occupation_agreement', 'no_unlisted_occupants', e.target.checked)}
            />
            I will not allow unlisted occupants
          </label>
          
          <label>
            <input
              type="checkbox"
              checked={formData.occupation_agreement.no_smoking}
              onChange={(e) => updateFormData('occupation_agreement', 'no_smoking', e.target.checked)}
            />
            I agree to no smoking policy
          </label>
          
          <label>
            <input
              type="checkbox"
              checked={formData.occupation_agreement.kitchen_cooking_only}
              onChange={(e) => updateFormData('occupation_agreement', 'kitchen_cooking_only', e.target.checked)}
            />
            I agree to use kitchen for cooking only
          </label>
        </div>
      </fieldset>

      {/* Consent and Declaration Section */}
      <fieldset style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
        <legend><strong>12. Consent & Declaration</strong></legend>
        
        <div style={{ marginBottom: '15px' }}>
          <h4>Consent</h4>
          <div style={{ marginBottom: '10px' }}>
            <label>
              <input
                type="checkbox"
                checked={formData.consent_and_declaration.consent_given}
                onChange={(e) => updateFormData('consent_and_declaration', 'consent_given', e.target.checked)}
              />
              I consent to the processing of my personal data as outlined in the privacy policy
            </label>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
            <div>
              <label htmlFor="consent_signature">Signature (Type name)</label>
              <input
                type="text"
                id="consent_signature"
                value={formData.consent_and_declaration.signature}
                onChange={(e) => updateFormData('consent_and_declaration', 'signature', e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
            
            <div>
              <label htmlFor="consent_date">Date</label>
              <input
                type="date"
                id="consent_date"
                value={formData.consent_and_declaration.date}
                onChange={(e) => updateFormData('consent_and_declaration', 'date', e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
            
            <div>
              <label htmlFor="consent_print_name">Print Name</label>
              <input
                type="text"
                id="consent_print_name"
                value={formData.consent_and_declaration.print_name}
                onChange={(e) => updateFormData('consent_and_declaration', 'print_name', e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
          </div>
        </div>
        
        <div>
          <h4>Declaration</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '10px' }}>
            <label>
              <input
                type="checkbox"
                checked={formData.consent_and_declaration.declaration.main_home}
                onChange={(e) => updateNestedFormData('consent_and_declaration', 'declaration', 'main_home', e.target.checked)}
              />
              This will be my main home
            </label>
            
            <label>
              <input
                type="checkbox"
                checked={formData.consent_and_declaration.declaration.enquiries_permission}
                onChange={(e) => updateNestedFormData('consent_and_declaration', 'declaration', 'enquiries_permission', e.target.checked)}
              />
              I give permission for enquiries to be made
            </label>
            
            <label>
              <input
                type="checkbox"
                checked={formData.consent_and_declaration.declaration.certify_no_judgements}
                onChange={(e) => updateNestedFormData('consent_and_declaration', 'declaration', 'certify_no_judgements', e.target.checked)}
              />
              I certify no outstanding county court judgements
            </label>
            
            <label>
              <input
                type="checkbox"
                checked={formData.consent_and_declaration.declaration.certify_no_housing_debt}
                onChange={(e) => updateNestedFormData('consent_and_declaration', 'declaration', 'certify_no_housing_debt', e.target.checked)}
              />
              I certify no housing-related debt
            </label>
            
            <label>
              <input
                type="checkbox"
                checked={formData.consent_and_declaration.declaration.certify_no_landlord_debt}
                onChange={(e) => updateNestedFormData('consent_and_declaration', 'declaration', 'certify_no_landlord_debt', e.target.checked)}
              />
              I certify no debt to previous landlords
            </label>
            
            <label>
              <input
                type="checkbox"
                checked={formData.consent_and_declaration.declaration.certify_no_abuse}
                onChange={(e) => updateNestedFormData('consent_and_declaration', 'declaration', 'certify_no_abuse', e.target.checked)}
              />
              I certify no history of property abuse
            </label>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
            <div>
              <label htmlFor="declaration_signature">Declaration Signature (Type name)</label>
              <input
                type="text"
                id="declaration_signature"
                value={formData.consent_and_declaration.declaration_signature}
                onChange={(e) => updateFormData('consent_and_declaration', 'declaration_signature', e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
            
            <div>
              <label htmlFor="declaration_date">Declaration Date</label>
              <input
                type="date"
                id="declaration_date"
                value={formData.consent_and_declaration.declaration_date}
                onChange={(e) => updateFormData('consent_and_declaration', 'declaration_date', e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
            
            <div>
              <label htmlFor="declaration_print_name">Declaration Print Name</label>
              <input
                type="text"
                id="declaration_print_name"
                value={formData.consent_and_declaration.declaration_print_name}
                onChange={(e) => updateFormData('consent_and_declaration', 'declaration_print_name', e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
          </div>
        </div>
      </fieldset>

      {/* Continue with other sections... */}
      {/* For brevity, I'll add the remaining sections in the next part */}
      
      <button type="submit" style={{ padding: '12px 24px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', fontSize: '16px' }}>
        Submit Application
      </button>
    </form>
  )
}

export default ApplicationFormFields
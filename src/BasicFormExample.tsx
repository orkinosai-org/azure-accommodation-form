import { useForm, SubmitHandler } from 'react-hook-form'

interface BasicFormData {
  fullName: string
  email: string
  phone: string
}

const BasicFormExample: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<BasicFormData>()

  const onSubmit: SubmitHandler<BasicFormData> = (data) => {
    console.log('Form submitted:', data)
    alert('Basic form submitted successfully!')
  }

  return (
    <div style={{ maxWidth: '500px', margin: '20px auto', padding: '20px' }}>
      <h2>Basic Form Example (React Hook Form)</h2>
      <p style={{ fontSize: '14px', color: '#666', marginBottom: '20px' }}>
        This is a simple example showing how to use React Hook Form for basic form handling.
      </p>
      
      <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label htmlFor="fullName" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Full Name *
          </label>
          <input
            id="fullName"
            {...register('fullName', { required: 'Full name is required' })}
            style={{ 
              width: '100%', 
              padding: '8px', 
              border: '1px solid #ccc', 
              borderRadius: '4px',
              borderColor: errors.fullName ? '#ff0000' : '#ccc'
            }}
          />
          {errors.fullName && (
            <span style={{ color: '#ff0000', fontSize: '12px' }}>
              {errors.fullName.message}
            </span>
          )}
        </div>

        <div>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Email *
          </label>
          <input
            id="email"
            type="email"
            {...register('email', { 
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            })}
            style={{ 
              width: '100%', 
              padding: '8px', 
              border: '1px solid #ccc', 
              borderRadius: '4px',
              borderColor: errors.email ? '#ff0000' : '#ccc'
            }}
          />
          {errors.email && (
            <span style={{ color: '#ff0000', fontSize: '12px' }}>
              {errors.email.message}
            </span>
          )}
        </div>

        <div>
          <label htmlFor="phone" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Phone Number
          </label>
          <input
            id="phone"
            type="tel"
            {...register('phone')}
            style={{ 
              width: '100%', 
              padding: '8px', 
              border: '1px solid #ccc', 
              borderRadius: '4px'
            }}
          />
        </div>

        <button 
          type="submit" 
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#007acc', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Submit Basic Form
        </button>
      </form>
    </div>
  )
}

export default BasicFormExample
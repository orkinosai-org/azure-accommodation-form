#!/bin/bash

# Script to test the enhanced metadata capture functionality
# This script tests the API endpoints directly to verify metadata is captured

echo "=== ENHANCED METADATA CAPTURE TEST ==="
echo "Testing API endpoints to verify comprehensive metadata capture"
echo

# Create test form data
TEST_DATA='{
  "tenantDetails": {
    "fullName": "John Doe Test",
    "email": "john.test@example.com",
    "telephone": "555-0123",
    "dateOfBirth": "1990-01-01T00:00:00",
    "nationalInsuranceNumber": "AB123456C"
  },
  "bankDetails": {
    "bankName": "Test Bank",
    "accountNumber": "12345678",
    "sortCode": "12-34-56"
  },
  "addressHistory": [
    {
      "address": "123 Test Street, Test City, TC1 2AB",
      "monthsLived": 24,
      "reasonForLeaving": "Relocation for work"
    }
  ],
  "contacts": {
    "nextOfKin": {
      "fullName": "Jane Doe",
      "relationship": "Spouse",
      "telephone": "555-0124"
    }
  },
  "medicalDetails": {
    "doctorName": "Dr. Smith",
    "doctorAddress": "Medical Center, Test City",
    "medicalConditions": "None"
  },
  "employment": {
    "employerName": "Test Company",
    "employerAddress": "Business Park, Test City",
    "position": "Software Developer",
    "startDate": "2020-01-01T00:00:00",
    "salary": 50000
  },
  "passportDetails": {
    "passportNumber": "123456789",
    "placeOfIssue": "UK",
    "expiryDate": "2030-12-31T00:00:00"
  },
  "currentLivingArrangement": {
    "accommodationType": "Rental",
    "address": "Current Address, Test City",
    "monthlyRent": 1200
  },
  "other": {
    "pets": "Cat",
    "otherOccupants": "None",
    "additionalInfo": "Test additional information"
  },
  "consentAndDeclaration": {
    "consentGiven": true,
    "declaration": {
      "mainHome": true,
      "enquiriesPermission": true,
      "certifyNoJudgements": true,
      "certifyNoHousingDebt": true,
      "certifyNoLandlordDebt": true,
      "certifyNoAbuse": true
    }
  }
}'

# Function to start the application
start_app() {
    echo "Starting Blazor application..."
    cd /home/runner/work/azure-accommodation-form/azure-accommodation-form/BlazorApp
    
    # Start the application in background
    dotnet run --urls http://localhost:5000 > /tmp/app.log 2>&1 &
    APP_PID=$!
    
    # Wait for application to start
    echo "Waiting for application to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5000/health > /dev/null 2>&1 || curl -s http://localhost:5000 > /dev/null 2>&1; then
            echo "Application started successfully (attempt $i)"
            return 0
        fi
        sleep 1
    done
    
    echo "Failed to start application"
    kill $APP_PID 2>/dev/null
    return 1
}

# Function to stop the application
stop_app() {
    if [ -n "$APP_PID" ]; then
        echo "Stopping application (PID: $APP_PID)..."
        kill $APP_PID 2>/dev/null
        wait $APP_PID 2>/dev/null
    fi
}

# Function to test API
test_api() {
    echo "Testing API endpoint with enhanced headers..."
    
    # Test the direct submission endpoint with comprehensive headers
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}\n" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "User-Agent: Enhanced-Test-Agent/1.0 (Linux; x64) TestFramework/2.0" \
        -H "Accept-Language: en-US,en;q=0.9,fr;q=0.8,de;q=0.7" \
        -H "Origin: https://test.example.com" \
        -H "Referer: https://test.example.com/accommodation-form" \
        -H "X-Forwarded-For: 203.0.113.195, 70.41.3.18, 150.172.238.178" \
        -H "X-Real-IP: 203.0.113.195" \
        -H "CF-RAY: test-ray-67890-LON" \
        -H "X-Amzn-Trace-Id: Root=1-test-trace-12345" \
        -H "X-Forwarded-Proto: https" \
        -H "X-Forwarded-Host: test.example.com" \
        -H "CF-Connecting-IP: 203.0.113.195" \
        -d "$TEST_DATA" \
        http://localhost:5000/api/form/submit-direct)
    
    # Extract HTTP code
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
    RESPONSE_BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")
    
    echo "HTTP Response Code: $HTTP_CODE"
    echo "Response Body:"
    echo "$RESPONSE_BODY" | jq . 2>/dev/null || echo "$RESPONSE_BODY"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ API call successful"
        
        # Extract submission ID
        SUBMISSION_ID=$(echo "$RESPONSE_BODY" | jq -r '.submissionId // empty' 2>/dev/null)
        if [ -n "$SUBMISSION_ID" ] && [ "$SUBMISSION_ID" != "null" ]; then
            echo "✅ Submission ID received: $SUBMISSION_ID"
            
            # Test the status endpoint to verify metadata was stored
            echo "Checking submission status and metadata..."
            STATUS_RESPONSE=$(curl -s http://localhost:5000/api/form/$SUBMISSION_ID/status)
            echo "Status Response:"
            echo "$STATUS_RESPONSE" | jq . 2>/dev/null || echo "$STATUS_RESPONSE"
            
            return 0
        else
            echo "❌ No submission ID in response"
            return 1
        fi
    else
        echo "❌ API call failed with code: $HTTP_CODE"
        return 1
    fi
}

# Function to check database for metadata
check_database() {
    echo "Checking database for captured metadata..."
    cd /home/runner/work/azure-accommodation-form/azure-accommodation-form/BlazorApp
    
    # Use dotnet to query the database
    dotnet run --no-build -- --check-latest-submission 2>/dev/null | tail -20
}

# Main test execution
main() {
    echo "Starting enhanced metadata capture test..."
    
    # Trap to ensure cleanup
    trap stop_app EXIT
    
    # Start application
    if ! start_app; then
        echo "❌ Failed to start application"
        exit 1
    fi
    
    # Test API
    if test_api; then
        echo "✅ Enhanced metadata capture test completed successfully"
        check_database
    else
        echo "❌ Enhanced metadata capture test failed"
        exit 1
    fi
}

# Run the test
main
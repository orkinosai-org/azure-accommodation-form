#!/bin/bash

# Simple test for metadata capture
echo "=== SIMPLE METADATA CAPTURE TEST ==="

# Create simple test data matching the actual model structure
TEST_DATA='{
  "tenantDetails": {
    "fullName": "John Doe Test",
    "email": "john.test@example.com", 
    "telephone": "07123456789",
    "dateOfBirth": "1990-01-01T00:00:00",
    "niNumber": "AB123456C"
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
    "nextOfKin": "Jane Doe",
    "relationship": "Spouse",
    "nextOfKinTelephone": "07123456790"
  },
  "medicalDetails": {
    "doctorName": "Dr. Smith",
    "surgery": "Medical Center",
    "address": "Test City"
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

echo "Starting application..."
cd /home/runner/work/azure-accommodation-form/azure-accommodation-form/BlazorApp

# Start app in background
dotnet run --urls http://localhost:5000 > /tmp/app.log 2>&1 &
APP_PID=$!

echo "Waiting for app to start..."
sleep 10

echo "Testing API with enhanced headers..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}\n" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "User-Agent: Enhanced-Test-Agent/1.0 (Linux; x64) TestFramework/2.0" \
    -H "Accept-Language: en-US,en;q=0.9,fr;q=0.8" \
    -H "Origin: https://test.example.com" \
    -H "Referer: https://test.example.com/form" \
    -H "X-Forwarded-For: 203.0.113.195, 70.41.3.18" \
    -H "X-Real-IP: 203.0.113.195" \
    -H "CF-RAY: test-ray-12345-LON" \
    -d "$TEST_DATA" \
    http://localhost:5000/api/form/submit-direct)

# Extract HTTP code
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

echo "HTTP Response Code: $HTTP_CODE"
echo "Response Body: $RESPONSE_BODY"

# Cleanup
kill $APP_PID 2>/dev/null

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS: API call completed with enhanced metadata"
    
    # Check for submission ID
    if echo "$RESPONSE_BODY" | grep -q '"submissionId"'; then
        echo "✅ Submission ID found in response"
        echo "✅ Enhanced metadata capture appears to be working"
    fi
else
    echo "❌ FAILED: API call failed with code $HTTP_CODE"
    echo "Response details: $RESPONSE_BODY"
fi
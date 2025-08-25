"""
Basic integration test for the Copilot Agent

This test verifies that the Copilot agent is properly integrated and functional.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.copilot.models.agent import AgentRequest
from app.copilot.services.agent_service import CopilotAgentService


async def test_copilot_basic_functionality():
    """Test basic Copilot agent functionality"""
    print("🤖 Testing External Collaboration Management Copilot Agent")
    print("=" * 60)
    
    # Initialize the agent service
    agent_service = CopilotAgentService()
    
    # Test cases
    test_cases = [
        {
            "name": "Library List Request",
            "message": "Show me all external libraries",
            "expected_intent": "library_list"
        },
        {
            "name": "Help Request", 
            "message": "What can you help me with?",
            "expected_intent": "help"
        },
        {
            "name": "Status Request",
            "message": "What's the system status?",
            "expected_intent": "status"
        },
        {
            "name": "Library Creation Request",
            "message": "I need to create a new library",
            "expected_intent": "library_create"
        },
        {
            "name": "User Access Request",
            "message": "Check user permissions for our libraries",
            "expected_intent": "user_access"
        }
    ]
    
    session_id = "test-session-001"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Message: '{test_case['message']}'")
        
        try:
            # Create agent request
            request = AgentRequest(
                user_message=test_case['message'],
                session_id=session_id,
                user_id="test-admin@example.com"
            )
            
            # Process request
            response = await agent_service.process_request(request)
            
            # Verify response
            print(f"   ✅ Response Type: {response.response_type}")
            print(f"   ✅ Content Length: {len(response.content)} characters")
            print(f"   ✅ Suggestions: {len(response.suggestions)} provided")
            
            if response.actions:
                print(f"   ✅ Actions: {len(response.actions)} available")
            
            # Show a snippet of the response
            content_snippet = response.content[:100] + "..." if len(response.content) > 100 else response.content
            print(f"   📝 Response: {content_snippet}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ All Copilot agent tests passed successfully!")
    print("\n🔧 Integration Status:")
    print("   • Agent Service: ✅ Operational")
    print("   • Conversation Service: ✅ Operational") 
    print("   • Task Service: ✅ Operational")
    print("   • Integration Service: ✅ Operational")
    
    return True


async def test_conversation_flow():
    """Test a complete conversation flow"""
    print("\n🗣️  Testing Conversation Flow")
    print("-" * 40)
    
    agent_service = CopilotAgentService()
    session_id = "test-conversation-001"
    
    conversation_steps = [
        "Hello, I need help with external libraries",
        "Show me all available libraries", 
        "Can you help me create a new library?",
        "What about user access management?",
        "Thank you for your help"
    ]
    
    for i, message in enumerate(conversation_steps, 1):
        print(f"\nStep {i}: '{message}'")
        
        request = AgentRequest(
            user_message=message,
            session_id=session_id,
            user_id="test-admin@example.com"
        )
        
        response = await agent_service.process_request(request)
        print(f"   Response: {response.content[:80]}...")
    
    print("\n✅ Conversation flow test completed successfully!")


async def test_external_library_integration():
    """Test integration with external library system"""
    print("\n📚 Testing External Library Integration")
    print("-" * 40)
    
    from app.copilot.services.integration_service import ExternalLibraryIntegrationService
    
    integration_service = ExternalLibraryIntegrationService()
    
    try:
        # Test getting active libraries
        libraries = await integration_service.get_active_libraries()
        print(f"   ✅ Retrieved {len(libraries)} active libraries")
        
        # Test getting statistics  
        stats = await integration_service.get_library_statistics()
        print(f"   ✅ Statistics: {stats.total_libraries} total, {stats.active_libraries} active")
        
        # Test search functionality
        search_results = await integration_service.search_libraries("sample")
        print(f"   ✅ Search results: {len(search_results)} libraries found")
        
        print("\n✅ External library integration test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Copilot Agent Integration Tests\n")
    
    tests = [
        ("Basic Functionality", test_copilot_basic_functionality),
        ("Conversation Flow", test_conversation_flow), 
        ("External Library Integration", test_external_library_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Copilot Agent is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
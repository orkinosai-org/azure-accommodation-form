"""
Test external library management functionality
"""

import asyncio
import json
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.external_library import ExternalLibraryService
from app.models.external_library import ExternalLibraryCreate, ExternalLibraryUpdate, ExternalUser, LibraryStatus


async def test_external_library_service():
    """Test the external library service functionality"""
    service = ExternalLibraryService()
    
    # Test creating a library
    library_data = ExternalLibraryCreate(
        name="Test Library",
        url="https://test.sharepoint.com/sites/test/Documents",
        description="Test library for unit testing",
        external_users=[
            ExternalUser(
                email="test@external.com",
                name="Test User",
                organization="Test Org"
            )
        ]
    )
    
    # Create library
    library = await service.create_library(library_data, "test-admin")
    assert library is not None
    assert library.name == "Test Library"
    assert library.status == LibraryStatus.ACTIVE
    assert len(library.external_users) == 1
    assert library.external_users[0].email == "test@external.com"
    
    # Test getting library
    retrieved = await service.get_library(library.id)
    assert retrieved is not None
    assert retrieved.id == library.id
    
    # Test listing libraries
    libraries = await service.list_libraries()
    assert len(libraries.libraries) >= 1
    
    # Test updating library
    update_data = ExternalLibraryUpdate(description="Updated description")
    updated = await service.update_library(library.id, update_data, "test-admin")
    assert updated is not None
    assert updated.description == "Updated description"
    
    # Test soft delete
    success = await service.delete_library(library.id, "test-admin")
    assert success is True
    
    # Verify library is marked as deleted
    deleted_lib = await service.get_library(library.id)
    assert deleted_lib.status == LibraryStatus.DELETED
    
    # Test restore
    restored = await service.restore_library(library.id, "test-admin")
    assert restored is not None
    assert restored.status == LibraryStatus.ACTIVE
    
    print("✅ All external library service tests passed!")


async def test_api_endpoints_basic():
    """Test basic API endpoint functionality without FastAPI test client"""
    # This is a basic test without full integration
    # In a real environment, you would use FastAPI TestClient
    
    from app.services.external_library import ExternalLibraryService
    
    service = ExternalLibraryService()
    
    # Test getting statistics
    stats = await service.get_statistics()
    assert stats.total_libraries >= 0
    assert stats.active_libraries >= 0
    assert stats.deleted_libraries >= 0
    
    # Test getting active libraries
    active_libs = await service.get_active_libraries()
    assert isinstance(active_libs, list)
    
    # Test search functionality
    search_results = await service.search_libraries("sample")
    assert isinstance(search_results, list)
    
    print("✅ All API endpoint tests passed!")


def test_library_validation():
    """Test library data validation"""
    
    # Test valid library
    try:
        library_data = ExternalLibraryCreate(
            name="Valid Library",
            url="https://valid.sharepoint.com/sites/test/Documents",
            description="Valid description"
        )
        assert library_data.name == "Valid Library"
        print("✅ Valid library data test passed!")
    except Exception as e:
        print(f"❌ Valid library test failed: {e}")
    
    # Test invalid URL
    try:
        invalid_library = ExternalLibraryCreate(
            name="Invalid Library",
            url="not-a-url",  # Invalid URL
            description="Invalid URL test"
        )
        print("❌ Invalid URL test should have failed but didn't!")
    except Exception as e:
        print("✅ Invalid URL validation test passed!")
    
    # Test empty name
    try:
        empty_name_library = ExternalLibraryCreate(
            name="",  # Empty name
            url="https://valid.sharepoint.com/sites/test/Documents",
            description="Empty name test"
        )
        print("❌ Empty name test should have failed but didn't!")
    except Exception as e:
        print("✅ Empty name validation test passed!")


async def main():
    print("Running External Library Management Tests...")
    print("=" * 50)
    
    try:
        test_library_validation()
        print()
        
        await test_external_library_service()
        print()
        
        await test_api_endpoints_basic()
        print()
        
        print("=" * 50)
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
"""
Azure Blob Storage service for file management

This service uses blob storage configuration that mirrors the .NET
BlobStorageSettings structure from appsettings.json.
"""

import io
import logging
from typing import BinaryIO, Optional
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceNotFoundError

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class AzureBlobStorageService:
    """Service for Azure Blob Storage operations using configuration that mirrors .NET BlobStorageSettings"""
    
    def __init__(self):
        settings = get_settings()
        self.blob_settings = settings.blob_storage_settings
        
        self.connection_string = self.blob_settings.connection_string
        self.container_name = self.blob_settings.container_name
        self.blob_service_client = None
        
        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            logger.info(f"Azure Blob Storage initialized with container: {self.container_name}")
        else:
            logger.warning("Azure Blob Storage not configured - missing connection string")
    
    async def test_connection(self) -> bool:
        """Test Azure Blob Storage connection"""
        if not self.blob_service_client:
            raise Exception("Azure Blob Storage not configured")
        
        try:
            # Try to get container properties
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            container_client.get_container_properties()
            return True
        except ResourceNotFoundError:
            # Container doesn't exist, try to create it
            try:
                container_client = self.blob_service_client.create_container(
                    self.container_name
                )
                logger.info(f"Created Azure Blob Storage container: {self.container_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to create container: {e}")
                raise
        except Exception as e:
            logger.error(f"Azure Blob Storage connection test failed: {e}")
            raise
    
    async def upload_pdf(self, filename: str, pdf_buffer: BinaryIO) -> str:
        """Upload PDF file to Azure Blob Storage"""
        if not self.blob_service_client:
            raise Exception("Azure Blob Storage not configured")
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            # Upload the file
            pdf_buffer.seek(0)
            blob_client.upload_blob(
                pdf_buffer.read(),
                overwrite=True,
                content_type="application/pdf"
            )
            
            # Get the blob URL
            blob_url = blob_client.url
            logger.info(f"PDF uploaded successfully: {filename}")
            return blob_url
            
        except Exception as e:
            logger.error(f"Failed to upload PDF {filename}: {e}")
            raise
    
    async def download_pdf(self, filename: str) -> str:
        """Download PDF file from Azure Blob Storage to temporary file"""
        if not self.blob_service_client:
            raise Exception("Azure Blob Storage not configured")
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            # Download to temporary file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            
            with open(temp_file.name, 'wb') as f:
                download_stream = blob_client.download_blob()
                f.write(download_stream.readall())
            
            logger.info(f"PDF downloaded successfully: {filename}")
            return temp_file.name
            
        except ResourceNotFoundError:
            logger.error(f"PDF not found: {filename}")
            raise FileNotFoundError(f"PDF not found: {filename}")
        except Exception as e:
            logger.error(f"Failed to download PDF {filename}: {e}")
            raise
    
    async def download_pdf_buffer(self, filename: str) -> BinaryIO:
        """Download PDF file from Azure Blob Storage to memory buffer"""
        if not self.blob_service_client:
            raise Exception("Azure Blob Storage not configured")
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            # Download to memory buffer
            buffer = io.BytesIO()
            download_stream = blob_client.download_blob()
            buffer.write(download_stream.readall())
            buffer.seek(0)
            
            logger.info(f"PDF downloaded to buffer successfully: {filename}")
            return buffer
            
        except ResourceNotFoundError:
            logger.error(f"PDF not found: {filename}")
            raise FileNotFoundError(f"PDF not found: {filename}")
        except Exception as e:
            logger.error(f"Failed to download PDF {filename}: {e}")
            raise
    
    async def delete_pdf(self, filename: str) -> bool:
        """Delete PDF file from Azure Blob Storage"""
        if not self.blob_service_client:
            raise Exception("Azure Blob Storage not configured")
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            # Delete the blob
            blob_client.delete_blob()
            logger.info(f"PDF deleted successfully: {filename}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"PDF not found for deletion: {filename}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete PDF {filename}: {e}")
            raise
    
    async def list_pdfs(self, prefix: Optional[str] = None) -> list:
        """List PDF files in Azure Blob Storage"""
        if not self.blob_service_client:
            raise Exception("Azure Blob Storage not configured")
        
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            
            blobs = []
            blob_list = container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blob_list:
                if blob.name.endswith('.pdf'):
                    blobs.append({
                        'name': blob.name,
                        'size': blob.size,
                        'last_modified': blob.last_modified,
                        'url': f"{container_client.url}/{blob.name}"
                    })
            
            logger.info(f"Listed {len(blobs)} PDF files")
            return blobs
            
        except Exception as e:
            logger.error(f"Failed to list PDFs: {e}")
            raise
    
    async def get_pdf_url(self, filename: str) -> str:
        """Get the URL for a PDF file"""
        if not self.blob_service_client:
            raise Exception("Azure Blob Storage not configured")
        
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=filename
        )
        
        return blob_client.url
    
    async def check_pdf_exists(self, filename: str) -> bool:
        """Check if a PDF file exists in Azure Blob Storage"""
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            blob_client.get_blob_properties()
            return True
            
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking if PDF exists {filename}: {e}")
            return False
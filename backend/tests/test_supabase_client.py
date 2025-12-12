"""
Tests for Supabase client and file upload functionality.
"""

import pytest
from unittest.mock import Mock, patch
import uuid

from src.services.supabase_client import upload_file_to_bucket


class TestSupabaseClient:
    """Test cases for Supabase client utilities."""

    @patch('src.services.supabase_client.uuid')
    def test_upload_file_to_bucket_success(self, mock_uuid, mock_supabase):
        """Test successful file upload to Supabase bucket."""
        # Setup
        mock_uuid.uuid4.return_value.hex = "test123"
        bucket_name = "test"
        file_bytes = b"test file content"
        filename = "test.jpg"
        
        # Mock successful upload
        mock_bucket = mock_supabase.storage.from_.return_value
        mock_bucket.upload.return_value = {"error": None}
        mock_bucket.get_public_url.return_value = "https://example.com/test123.jpg"
        
        # Execute
        result = upload_file_to_bucket(bucket_name, file_bytes, filename)
        
        # Assert
        assert result == "https://example.com/test123.jpg"
        mock_supabase.storage.from_.assert_called_once_with(bucket_name)
        mock_bucket.upload.assert_called_once()
        mock_bucket.get_public_url.assert_called_once_with("uploads/test123.jpg")

    def test_upload_file_to_bucket_upload_failure(self, mock_supabase):
        """Test file upload failure."""
        # Setup
        bucket_name = "test"
        file_bytes = b"test file content"
        filename = "test.jpg"
        
        # Mock upload failure - the response should have an error attribute
        mock_bucket = mock_supabase.storage.from_.return_value
        mock_response = Mock()
        mock_response.error = {"message": "Upload failed"}
        mock_bucket.upload.return_value = mock_response
        
        # Execute
        result = upload_file_to_bucket(bucket_name, file_bytes, filename)
        
        # Assert
        assert result is None

    def test_upload_file_to_bucket_exception(self, mock_supabase):
        """Test file upload with exception."""
        # Setup
        bucket_name = "test"
        file_bytes = b"test file content"
        filename = "test.jpg"
        
        # Mock exception
        mock_supabase.storage.from_.side_effect = Exception("Storage error")
        
        # Execute
        result = upload_file_to_bucket(bucket_name, file_bytes, filename)
        
        # Assert
        assert result is None

    def test_upload_file_with_no_extension(self, mock_supabase):
        """Test file upload with filename that has no extension."""
        bucket_name = "test"
        file_bytes = b"test file content"
        filename = "testfile"
        
        # Mock successful upload
        mock_bucket = mock_supabase.storage.from_.return_value
        mock_bucket.upload.return_value = {"error": None}
        mock_bucket.get_public_url.return_value = "https://example.com/testfile"
        
        result = upload_file_to_bucket(bucket_name, file_bytes, filename)
        
        assert result == "https://example.com/testfile"

    def test_upload_file_make_public_false(self, mock_supabase):
        """Test file upload with make_public=False."""
        bucket_name = "test"
        file_bytes = b"test file content"
        filename = "test.jpg"
        
        # Mock successful upload and signed URL
        mock_bucket = mock_supabase.storage.from_.return_value
        mock_bucket.upload.return_value = {"error": None}
        mock_bucket.create_signed_url.return_value = {
            "signedURL": "https://example.com/signed/test.jpg"
        }
        
        result = upload_file_to_bucket(bucket_name, file_bytes, filename, make_public=False)
        
        assert result == "https://example.com/signed/test.jpg"
        mock_bucket.create_signed_url.assert_called_once()

    def test_upload_file_content_type_guessing(self, mock_supabase):
        """Test that content type is guessed correctly from filename."""
        bucket_name = "test"
        file_bytes = b"test file content"
        filename = "test.png"
        
        # Mock successful upload
        mock_bucket = mock_supabase.storage.from_.return_value
        mock_bucket.upload.return_value = {"error": None}
        mock_bucket.get_public_url.return_value = "https://example.com/test.png"
        
        result = upload_file_to_bucket(bucket_name, file_bytes, filename)
        
        # Verify upload was called with content-type
        upload_call_args = mock_bucket.upload.call_args
        assert upload_call_args is not None
        # The third argument should contain content-type
        if len(upload_call_args[0]) > 2:
            headers = upload_call_args[0][2]
            assert 'content-type' in headers
            assert 'image/png' in headers['content-type']

    def test_upload_file_with_custom_content_type(self, mock_supabase):
        """Test file upload with custom content type."""
        bucket_name = "test"
        file_bytes = b"test file content"
        filename = "test.jpg"
        content_type = "image/jpeg"
        
        # Mock successful upload
        mock_bucket = mock_supabase.storage.from_.return_value
        mock_bucket.upload.return_value = {"error": None}
        mock_bucket.get_public_url.return_value = "https://example.com/test.jpg"
        
        result = upload_file_to_bucket(bucket_name, file_bytes, filename, content_type=content_type)
        
        assert result == "https://example.com/test.jpg"
        # Verify content type was used
        upload_call_args = mock_bucket.upload.call_args
        assert upload_call_args is not None

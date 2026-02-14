"""Test workspace restriction functionality."""
import os
import tempfile
import pytest
from python.helpers import files, settings


def test_validate_workspace_path_disabled():
    """Test that validation passes when workspace restriction is disabled."""
    # Mock settings to disable workspace restriction
    original_get_settings = settings.get_settings
    
    def mock_get_settings():
        return {
            "workspace_restrict_enabled": False,
            "workspace_root_path": "/some/path"
        }
    
    settings.get_settings = mock_get_settings
    
    try:
        # Should pass validation
        is_valid, error_msg = files.validate_workspace_path("/tmp/outside")
        assert is_valid is True
        assert error_msg == ""
    finally:
        settings.get_settings = original_get_settings


def test_validate_workspace_path_enabled_within_workspace():
    """Test that validation passes for paths within workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = tmpdir
        test_path = os.path.join(tmpdir, "subdir", "file.txt")
        
        original_get_settings = settings.get_settings
        
        def mock_get_settings():
            return {
                "workspace_restrict_enabled": True,
                "workspace_root_path": workspace_root
            }
        
        settings.get_settings = mock_get_settings
        
        try:
            # Should pass validation
            is_valid, error_msg = files.validate_workspace_path(test_path)
            assert is_valid is True
            assert error_msg == ""
        finally:
            settings.get_settings = original_get_settings


def test_validate_workspace_path_enabled_outside_workspace():
    """Test that validation fails for paths outside workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = os.path.join(tmpdir, "workspace")
        os.makedirs(workspace_root, exist_ok=True)
        
        # Path outside workspace
        outside_path = os.path.join(tmpdir, "outside", "file.txt")
        
        original_get_settings = settings.get_settings
        
        def mock_get_settings():
            return {
                "workspace_restrict_enabled": True,
                "workspace_root_path": workspace_root
            }
        
        settings.get_settings = mock_get_settings
        
        try:
            # Should fail validation
            is_valid, error_msg = files.validate_workspace_path(outside_path)
            assert is_valid is False
            assert "Access denied" in error_msg
            assert "outside the workspace boundary" in error_msg
        finally:
            settings.get_settings = original_get_settings


def test_validate_workspace_path_directory_traversal():
    """Test that directory traversal attempts are blocked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = os.path.join(tmpdir, "workspace")
        os.makedirs(workspace_root, exist_ok=True)
        
        # Attempt to use ../ to escape workspace
        traversal_path = os.path.join(workspace_root, "..", "..", "etc", "passwd")
        
        original_get_settings = settings.get_settings
        
        def mock_get_settings():
            return {
                "workspace_restrict_enabled": True,
                "workspace_root_path": workspace_root
            }
        
        settings.get_settings = mock_get_settings
        
        try:
            # Should fail validation
            is_valid, error_msg = files.validate_workspace_path(traversal_path)
            assert is_valid is False
            assert "Access denied" in error_msg
        finally:
            settings.get_settings = original_get_settings


def test_file_operations_respect_workspace_boundary():
    """Test that file operations respect workspace boundary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = os.path.join(tmpdir, "workspace")
        os.makedirs(workspace_root, exist_ok=True)
        
        # Path outside workspace
        outside_path = os.path.join(tmpdir, "outside")
        os.makedirs(outside_path, exist_ok=True)
        outside_file = os.path.join(outside_path, "file.txt")
        
        # Create a test file outside workspace
        with open(outside_file, "w") as f:
            f.write("test content")
        
        original_get_settings = settings.get_settings
        original_get_abs_path = files.get_abs_path
        
        def mock_get_settings():
            return {
                "workspace_restrict_enabled": True,
                "workspace_root_path": workspace_root
            }
        
        def mock_get_abs_path(*paths):
            # Return the joined path without modifying it
            return os.path.join(*paths)
        
        settings.get_settings = mock_get_settings
        files.get_abs_path = mock_get_abs_path
        
        try:
            # Attempt to read file outside workspace should raise PermissionError
            with pytest.raises(PermissionError) as exc_info:
                files.read_file(outside_file)
            
            assert "Access denied" in str(exc_info.value)
            assert "outside the workspace boundary" in str(exc_info.value)
            
            # Attempt to write file outside workspace should raise PermissionError
            with pytest.raises(PermissionError) as exc_info:
                files.write_file(outside_file, "new content")
            
            assert "Access denied" in str(exc_info.value)
            
        finally:
            settings.get_settings = original_get_settings
            files.get_abs_path = original_get_abs_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

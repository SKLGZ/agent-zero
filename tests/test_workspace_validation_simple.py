"""Simple test to verify workspace path validation logic."""
import os
import sys
import tempfile

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_workspace_validation():
    """Test workspace path validation without full module dependencies."""
    
    def is_in_dir(path: str, dir: str):
        """Check if the given path is within the directory."""
        abs_path = os.path.abspath(path)
        abs_dir = os.path.abspath(dir)
        return os.path.commonpath([abs_path, abs_dir]) == abs_dir
    
    def validate_workspace_path(path: str, workspace_root: str, enabled: bool) -> tuple[bool, str]:
        """Validate if a path is within the workspace boundary."""
        if not enabled:
            return True, ""
        
        if not workspace_root:
            return True, ""
        
        abs_path = os.path.abspath(path)
        abs_workspace = os.path.abspath(workspace_root)
        
        if not is_in_dir(abs_path, abs_workspace):
            return False, f"Access denied: Path '{path}' is outside the workspace boundary '{workspace_root}'"
        
        return True, ""
    
    print("Running workspace validation tests...")
    
    # Test 1: Validation disabled
    print("\nTest 1: Validation disabled")
    is_valid, error_msg = validate_workspace_path("/tmp/outside", "/home/workspace", False)
    assert is_valid is True, "Should pass when validation is disabled"
    assert error_msg == "", "Error message should be empty"
    print("✓ PASS: Validation disabled allows any path")
    
    # Test 2: Path within workspace
    print("\nTest 2: Path within workspace")
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = tmpdir
        test_path = os.path.join(tmpdir, "subdir", "file.txt")
        
        is_valid, error_msg = validate_workspace_path(test_path, workspace_root, True)
        assert is_valid is True, "Should pass for paths within workspace"
        assert error_msg == "", "Error message should be empty"
        print(f"✓ PASS: Path within workspace allowed")
        print(f"  Workspace: {workspace_root}")
        print(f"  Path: {test_path}")
    
    # Test 3: Path outside workspace
    print("\nTest 3: Path outside workspace")
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = os.path.join(tmpdir, "workspace")
        os.makedirs(workspace_root, exist_ok=True)
        
        outside_path = os.path.join(tmpdir, "outside", "file.txt")
        
        is_valid, error_msg = validate_workspace_path(outside_path, workspace_root, True)
        assert is_valid is False, "Should fail for paths outside workspace"
        assert "Access denied" in error_msg, "Error message should contain 'Access denied'"
        assert "outside the workspace boundary" in error_msg, "Error message should mention boundary"
        print(f"✓ PASS: Path outside workspace blocked")
        print(f"  Workspace: {workspace_root}")
        print(f"  Path: {outside_path}")
        print(f"  Error: {error_msg}")
    
    # Test 4: Directory traversal attempt
    print("\nTest 4: Directory traversal attempt")
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = os.path.join(tmpdir, "workspace")
        os.makedirs(workspace_root, exist_ok=True)
        
        # Attempt to use ../ to escape workspace
        traversal_path = os.path.join(workspace_root, "..", "..", "etc", "passwd")
        
        is_valid, error_msg = validate_workspace_path(traversal_path, workspace_root, True)
        assert is_valid is False, "Should fail for directory traversal attempts"
        assert "Access denied" in error_msg, "Error message should contain 'Access denied'"
        print(f"✓ PASS: Directory traversal blocked")
        print(f"  Workspace: {workspace_root}")
        print(f"  Traversal attempt: {traversal_path}")
        print(f"  Resolved to: {os.path.abspath(traversal_path)}")
        print(f"  Error: {error_msg}")
    
    # Test 5: Same directory (edge case)
    print("\nTest 5: Same directory (edge case)")
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = tmpdir
        
        is_valid, error_msg = validate_workspace_path(workspace_root, workspace_root, True)
        assert is_valid is True, "Should pass for workspace root itself"
        assert error_msg == "", "Error message should be empty"
        print(f"✓ PASS: Workspace root itself is allowed")
    
    print("\n" + "="*60)
    print("All tests PASSED! ✓")
    print("="*60)


if __name__ == "__main__":
    test_workspace_validation()

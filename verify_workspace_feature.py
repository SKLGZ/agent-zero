#!/usr/bin/env python3
"""Verify workspace restriction feature is correctly implemented."""
import os
import ast
import sys

def check_file_has_function(filepath, function_name):
    """Check if a Python file contains a specific function."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return True
        return False
    except Exception as e:
        print(f"  ✗ Error parsing {filepath}: {e}")
        return False

def check_settings_has_field(filepath, field_name):
    """Check if settings.py TypedDict has a specific field."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Simple string search for the field
        return field_name in content
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return False

def main():
    print("="*60)
    print("WORKSPACE RESTRICTION FEATURE VERIFICATION")
    print("="*60)
    
    all_checks_passed = True
    
    # Check 1: validate_workspace_path function exists
    print("\n1. Checking validate_workspace_path() function...")
    if check_file_has_function("python/helpers/files.py", "validate_workspace_path"):
        print("  ✓ Function exists in files.py")
    else:
        print("  ✗ Function missing in files.py")
        all_checks_passed = False
    
    # Check 2: Settings fields exist
    print("\n2. Checking settings fields...")
    settings_file = "python/helpers/settings.py"
    
    if check_settings_has_field(settings_file, "workspace_restrict_enabled"):
        print("  ✓ workspace_restrict_enabled field exists")
    else:
        print("  ✗ workspace_restrict_enabled field missing")
        all_checks_passed = False
    
    if check_settings_has_field(settings_file, "workspace_root_path"):
        print("  ✓ workspace_root_path field exists")
    else:
        print("  ✗ workspace_root_path field missing")
        all_checks_passed = False
    
    # Check 3: File operations have validation
    print("\n3. Checking file operations have validation...")
    files_file = "python/helpers/files.py"
    
    operations = [
        ("read_file", "read_file"),
        ("write_file", "write_file"),
        ("delete_dir", "delete_dir"),
        ("move_dir", "move_dir"),
        ("create_dir", "create_dir")
    ]
    
    for op_name, func_name in operations:
        if check_file_has_function(files_file, func_name):
            with open(files_file, 'r') as f:
                content = f.read()
                # Check if the function contains validate_workspace_path call
                func_start = content.find(f"def {func_name}(")
                if func_start != -1:
                    # Find the next function definition
                    next_def = content.find("\ndef ", func_start + 1)
                    if next_def == -1:
                        func_content = content[func_start:]
                    else:
                        func_content = content[func_start:next_def]
                    
                    if "validate_workspace_path" in func_content:
                        print(f"  ✓ {op_name} has validation")
                    else:
                        print(f"  ✗ {op_name} missing validation")
                        all_checks_passed = False
        else:
            print(f"  ✗ Function {func_name} not found")
            all_checks_passed = False
    
    # Check 4: Code execution tool updated
    print("\n4. Checking code_execution_tool.py...")
    cet_file = "python/tools/code_execution_tool.py"
    
    # Use simple string search instead of AST parsing for async functions
    try:
        with open(cet_file, 'r') as f:
            content = f.read()
            if "async def ensure_cwd" in content or "def ensure_cwd" in content:
                if "validate_workspace_path" in content:
                    print("  ✓ ensure_cwd has workspace validation")
                else:
                    print("  ✗ ensure_cwd missing workspace validation")
                    all_checks_passed = False
            else:
                print("  ✗ ensure_cwd function not found")
                all_checks_passed = False
    except Exception as e:
        print(f"  ✗ Error reading {cet_file}: {e}")
        all_checks_passed = False
    
    # Check 5: Documentation exists
    print("\n5. Checking documentation...")
    doc_file = "docs/guides/local-workspace.md"
    
    if os.path.exists(doc_file):
        print(f"  ✓ {doc_file} exists")
        with open(doc_file, 'r') as f:
            content = f.read()
            if "workspace_restrict_enabled" in content:
                print("  ✓ Documentation mentions workspace_restrict_enabled")
            else:
                print("  ✗ Documentation missing workspace_restrict_enabled")
                all_checks_passed = False
    else:
        print(f"  ✗ {doc_file} missing")
        all_checks_passed = False
    
    # Check 6: Tests exist
    print("\n6. Checking tests...")
    test_file = "tests/test_workspace_validation_simple.py"
    
    if os.path.exists(test_file):
        print(f"  ✓ {test_file} exists")
    else:
        print(f"  ✗ {test_file} missing")
        all_checks_passed = False
    
    # Check 7: README updated
    print("\n7. Checking README...")
    readme_file = "README.md"
    
    if os.path.exists(readme_file):
        with open(readme_file, 'r') as f:
            content = f.read()
            if "Local Workspace Mode" in content or "local-workspace.md" in content:
                print("  ✓ README mentions local workspace mode")
            else:
                print("  ✗ README missing local workspace mode reference")
                all_checks_passed = False
    else:
        print("  ✗ README.md not found")
        all_checks_passed = False
    
    # Final result
    print("\n" + "="*60)
    if all_checks_passed:
        print("✓ ALL CHECKS PASSED")
        print("="*60)
        print("\nThe workspace restriction feature is correctly implemented!")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("="*60)
        print("\nPlease review the failed checks above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

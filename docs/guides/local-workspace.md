# Local Workspace Mode

Agent Zero can run in local workspace mode without Docker, allowing you to specify a desktop folder as your project workspace while ensuring the agent operates securely within that boundary.

## Overview

Local workspace mode provides:
- **No Docker Required**: Run Agent Zero directly on your local machine
- **Custom Workspace**: Select any desktop folder as your project workspace
- **Security Sandbox**: Agent operations are restricted to your chosen workspace directory
- **Easy Setup**: Simple configuration with minimal dependencies

## Configuration

### Environment Variables

You can configure workspace settings using environment variables in your `.env` file:

```bash
# Enable workspace restriction (default: true for non-Docker mode)
A0_SET_workspace_restrict_enabled=true

# Set your workspace root path (default: usr/)
A0_SET_workspace_root_path=/home/username/Desktop/my-agent-workspace

# Use local shell interface instead of SSH (default for non-Docker)
A0_SET_shell_interface=local

# Set working directory within workspace (default: usr/workdir)
A0_SET_workdir_path=/home/username/Desktop/my-agent-workspace/workdir
```

### Settings UI

You can also configure workspace settings through the web UI:

1. Navigate to **Settings** in the web interface
2. Find the **Workspace** section
3. Set **Workspace Root Path** to your desired folder
4. Enable **Workspace Restriction** to enforce security boundaries
5. Set **Shell Interface** to `local` for direct local execution

## Security Features

### Path Validation

When workspace restriction is enabled, Agent Zero validates all file operations to ensure they stay within the workspace boundary:

- ✅ **Allowed**: Reading/writing files within workspace
- ✅ **Allowed**: Creating subdirectories within workspace
- ❌ **Blocked**: Accessing files outside workspace
- ❌ **Blocked**: Directory traversal attempts (e.g., `../../../etc/passwd`)
- ❌ **Blocked**: Symbolic links pointing outside workspace

### Protected Operations

The following operations are protected by workspace validation:

- `read_file()` - Reading file contents
- `write_file()` - Writing file contents
- `delete_dir()` - Deleting directories
- `move_dir()` - Moving/renaming directories
- `create_dir()` - Creating new directories
- Code execution working directory

### Validation Logic

The validation uses `os.path.commonpath()` to ensure paths are within the workspace:

```python
def validate_workspace_path(path: str) -> tuple[bool, str]:
    """
    Validate if a path is within the workspace boundary.
    Returns (is_valid, error_message)
    """
    abs_path = os.path.abspath(path)
    abs_workspace = os.path.abspath(workspace_root)
    
    if not is_in_dir(abs_path, abs_workspace):
        return False, "Access denied: Path is outside workspace boundary"
    
    return True, ""
```

This approach:
- Resolves all relative paths to absolute paths
- Prevents `../` directory traversal attacks
- Uses standard library functions for cross-platform compatibility

## Setup Instructions

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/SKLGZ/agent-zero.git
cd agent-zero

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Workspace

Create a `.env` file in the project root:

```bash
# Workspace configuration
A0_SET_workspace_restrict_enabled=true
A0_SET_workspace_root_path=/home/username/Desktop/my-projects
A0_SET_shell_interface=local

# API keys (required)
API_KEY_OPENROUTER=your-api-key-here
```

### 3. Create Workspace Directory

```bash
# Create your workspace folder
mkdir -p /home/username/Desktop/my-projects
mkdir -p /home/username/Desktop/my-projects/workdir
```

### 4. Run Agent Zero

```bash
# Start the web UI
python run_ui.py
```

Visit `http://localhost:50001` to access the web interface.

## Use Cases

### Software Development

Set up a workspace for a specific project:

```bash
A0_SET_workspace_root_path=/home/username/Desktop/my-app
A0_SET_workdir_path=/home/username/Desktop/my-app/src
```

The agent can:
- Read and modify source files
- Run tests and build commands
- Create new files and directories
- But **cannot** access files outside `/home/username/Desktop/my-app`

### Data Analysis

Work with data in a specific folder:

```bash
A0_SET_workspace_root_path=/home/username/Desktop/data-project
A0_SET_workdir_path=/home/username/Desktop/data-project/data
```

The agent can:
- Process CSV/JSON files
- Generate reports and visualizations
- Save analysis results
- But **cannot** access other data folders on your system

### Document Processing

Process documents in a dedicated folder:

```bash
A0_SET_workspace_root_path=/home/username/Desktop/documents
```

The agent can:
- Read and analyze documents
- Generate summaries
- Extract information
- But **cannot** access sensitive files elsewhere

## Troubleshooting

### Permission Errors

If you see "Access denied: Path is outside workspace boundary":

1. Check your `workspace_root_path` setting
2. Ensure the path you're accessing is within the workspace
3. Verify workspace restriction is configured correctly

### Path Issues on Windows

On Windows, use forward slashes or escape backslashes:

```bash
# Good
A0_SET_workspace_root_path=C:/Users/username/Desktop/workspace

# Also good
A0_SET_workspace_root_path=C:\\Users\\username\\Desktop\\workspace
```

### Workspace Not Applied

If changes don't take effect:

1. Restart the Agent Zero server
2. Clear browser cache
3. Check `.env` file is in the project root
4. Verify environment variable names start with `A0_SET_`

## Comparison: Docker vs Local Mode

| Feature | Docker Mode | Local Mode |
|---------|-------------|------------|
| Setup Complexity | High (Docker required) | Low (Python only) |
| Isolation | Strong (container) | Moderate (path validation) |
| Performance | Overhead from virtualization | Native performance |
| File Access | Mounted volumes | Direct file system access |
| Portability | High (containerized) | Platform-dependent |
| Resource Usage | Higher (container overhead) | Lower (native) |
| Security | Container isolation + path validation | Path validation only |

## Best Practices

1. **Use Dedicated Workspace**: Create a specific folder for Agent Zero projects
2. **Enable Restriction**: Always enable `workspace_restrict_enabled` for security
3. **Backup Important Data**: Keep backups outside the workspace
4. **Regular Updates**: Keep Agent Zero updated for security patches
5. **Monitor Activities**: Review agent actions and logs regularly
6. **Limit Scope**: Use narrow workspace paths for specific tasks

## Advanced Configuration

### Multiple Workspaces

You can use Agent Zero's project system with different workspaces:

1. Create multiple project folders within your workspace root
2. Switch between projects in the UI
3. Each project can have its own instructions and settings

### Custom Validation

For advanced use cases, you can modify the validation logic in:

```
python/helpers/files.py:validate_workspace_path()
```

### Integration with IDEs

You can integrate Agent Zero with your IDE by:

1. Setting workspace to your project root
2. Configuring IDE to watch workspace changes
3. Using Agent Zero as an assistant within your development workflow

## Frequently Asked Questions

**Q: Can I disable workspace restriction?**

A: Yes, set `A0_SET_workspace_restrict_enabled=false`, but this is not recommended for security.

**Q: What happens if the agent tries to access files outside the workspace?**

A: The operation will fail with a `PermissionError` and the agent will receive an error message.

**Q: Can I use relative paths?**

A: Yes, relative paths are resolved relative to the workspace root.

**Q: Does this work on Windows, macOS, and Linux?**

A: Yes, the path validation uses cross-platform Python functions.

**Q: Can I change the workspace path while Agent Zero is running?**

A: Yes, update the setting in the UI and it will take effect immediately.

## Related Documentation

- [Installation Guide](../setup/installation.md)
- [Usage Guide](usage.md)
- [Projects](projects.md)
- [Troubleshooting](troubleshooting.md)

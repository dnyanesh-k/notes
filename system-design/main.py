
def main():
    """Test the change analyzer."""
    print("Step 1.2b: Change Analyzer - Part 1")
    print("=" * 50)
    
    if not is_git_repo(repo_path="/home/dnyaneshwar/project/notes"):
        print("❌ Not a git repository")
        return
    
    # Get changed files
    changed_files = get_changed_files(repo_path="/home/dnyaneshwar/project/notes")
    
    if not changed_files:
        print("📝 No changed files to analyze")
        return
    
    print(f"📝 Analyzing {len(changed_files)} changed file(s):\n")
    
    # Analyze first 3 files as example
    for file_path in changed_files[:3]:
        status = get_change_status(file_path)
        diff = get_file_diff(file_path)
        
        print(f"File: {file_path}")
        print(f"  Status: {status}")
        print(f"  Diff lines: {len(diff.splitlines())} lines")
        
        # Show first few lines of diff
        if diff:
            first_lines = diff.split('\n')[:5]
            print(f"  Preview:")
            for line in first_lines:
                print(f"    {line[:60]}")  # Truncate long lines
        
        print()
    
    if len(changed_files) > 3:
        print(f"... and {len(changed_files) - 3} more files")
    
    print("=" * 50)
    print("✅ Change analysis working!")
    print("\nWhat we learned:")
    print("  - git diff for actual change content")
    print("  - git diff --name-status for change type")
    print("  - Parsing git output")


if __name__ == "__main__":
    main()

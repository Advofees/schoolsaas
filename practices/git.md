# Initial Setup
```bash
# Make sure you're on main branch and it's up to date
git checkout main
git pull
```

# Creating & Working on a Feature Branch
```bash
# Create and switch to new feature branch
git checkout -b feat-postings-invoice

# Push the new branch to remote and set upstream
git push -u origin feat-postings-invoice

# Useful commands while working
git branch    # Check which branch you're on
git status    # See what files have changed

# Committing your changes
git add --all                         # Stage all changes
git commit -m "my commit message"     # Commit changes
git push                             # Push to remote
```

# Merging Main into Your Feature Branch
```bash
# First, update main
git checkout main
git pull

# Switch to your feature branch and merge main
git checkout feat-auth
git merge --no-ff main -m "merging main"

# If there are NO conflicts:
git push

# If there ARE conflicts:
# 1. Resolve conflicts in your editor
# 2. Stage and commit the resolved changes
git add --all
git commit -m "solving conflicts"
git push
```

# Final Step
- Create a Pull Request (PR) on GitHub to merge your feature branch into main

This workflow assumes you're:
1. Starting from main
2. Creating a feature branch
3. Making changes
4. Keeping your feature branch up-to-date with main
5. Finally creating a PR to merge your changes back to main
dads# Git Repository Setup Guide

Your git repository has been initialized! Here's what was done and next steps:

## ✅ What's Been Done

1. **Git repository initialized** - `.git/` directory created
2. **All files staged** - All project files are ready to commit
3. **Initial commit created** - All code is now tracked in git
4. **`.gitignore` configured** - Excludes:
   - Python cache files (`__pycache__/`, `*.pyc`)
   - Virtual environments (`venv/`, `.venv/`)
   - Simulation outputs (`runs/`, `*.parquet`)
   - IDE files (`.vscode/`, `.idea/`)
   - OS files (`.DS_Store`)

## 📋 Next Steps

### 1. Create a Remote Repository (GitHub/GitLab)

**Option A: GitHub**
1. Go to https://github.com/new
2. Create a new repository (e.g., `misinformation-simulation`)
3. **Don't** initialize with README (you already have one)
4. Copy the repository URL

**Option B: GitLab**
1. Go to https://gitlab.com/projects/new
2. Create a new project
3. Copy the repository URL

### 2. Connect Your Local Repository to Remote

```bash
# Add remote repository (replace URL with your actual repository URL)
git remote add origin https://github.com/YOUR_USERNAME/misinformation-simulation.git

# Or for SSH:
git remote add origin git@github.com:YOUR_USERNAME/misinformation-simulation.git
```

### 3. Push Your Code

```bash
# Push to remote repository
git push -u origin main

# If you get an error about branch name, try:
git branch -M main
git push -u origin main
```

### 4. Verify Remote Connection

```bash
# Check remote URL
git remote -v

# View all branches
git branch -a
```

## 🔄 Common Git Commands

### Daily Workflow

```bash
# Check status
git status

# See what changed
git diff

# Stage changes
git add <file>           # Add specific file
git add .                # Add all changes

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push

# Pull latest changes
git pull
```

### Viewing History

```bash
# View commit history
git log

# View compact history
git log --oneline --graph

# View changes in a file
git log -p <file>
```

### Branching (for features)

```bash
# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch
git checkout main
git merge feature-name

# Delete branch
git branch -d feature-name
```

## 📝 Making Changes

1. **Make your changes** to files
2. **Stage changes**: `git add .` or `git add <specific-files>`
3. **Commit**: `git commit -m "Description of what changed"`
4. **Push**: `git push`

## 🚫 What's Ignored

The `.gitignore` file excludes:
- `runs/` - Simulation output files (too large for git)
- `*.parquet` - Data files
- `__pycache__/` - Python cache
- `venv/` - Virtual environments
- IDE and OS files

## 💡 Tips

- **Commit often** - Small, frequent commits are better than large ones
- **Write clear commit messages** - Describe what and why, not how
- **Pull before push** - Always pull latest changes before pushing
- **Use branches** - Create branches for new features to keep main stable

## 🔗 Useful Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [GitLab Documentation](https://docs.gitlab.com/)

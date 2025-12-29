#!/bin/bash
# Script to push to a new GitHub repository
# Usage: ./push_to_new_repo.sh YOUR_USERNAME REPO_NAME

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./push_to_new_repo.sh YOUR_USERNAME REPO_NAME"
    echo "Example: ./push_to_new_repo.sh johndoe misinformation-simulation"
    exit 1
fi

USERNAME=$1
REPO_NAME=$2

echo "Removing old remote..."
git remote remove origin

echo "Adding new remote: https://github.com/$USERNAME/$REPO_NAME.git"
git remote add origin https://github.com/$USERNAME/$REPO_NAME.git

echo "Pushing to new repository..."
git push -u origin main

echo "Done! Your code is now at: https://github.com/$USERNAME/$REPO_NAME"

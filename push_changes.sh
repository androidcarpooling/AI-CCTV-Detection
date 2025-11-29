#!/bin/bash
cd /home/isha/face_recognition_system
echo "Current directory: $(pwd)"
echo "Git status:"
git status --short
echo ""
echo "Adding all changes..."
git add -A
echo "Committing..."
git commit -m "Fix Railway: Lazy load processor, add health check endpoint" || echo "Nothing to commit"
echo "Pushing to GitHub..."
git push origin main
echo "Done!"


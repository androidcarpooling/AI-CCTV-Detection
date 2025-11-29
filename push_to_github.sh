#!/bin/bash
# Script to push code to GitHub and trigger Railway deployment

cd /home/isha/face_recognition_system

echo "Adding all changes..."
git add -A

echo "Committing changes..."
git commit -m "Fix Railway deployment: Dockerfile for Debian Trixie, PORT env var, Railway config"

echo "Pushing to GitHub..."
git push origin main

echo "Done! Railway should auto-deploy now."


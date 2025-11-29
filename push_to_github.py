#!/usr/bin/env python3
import subprocess
import os
import sys

os.chdir('/home/isha/face_recognition_system')

print("=== Git Status ===")
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

print("\n=== Adding files ===")
result = subprocess.run(['git', 'add', '-A'], capture_output=True, text=True)
if result.stdout:
    print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

print("\n=== Committing ===")
result = subprocess.run(['git', 'commit', '-m', 'Fix Railway: Lazy load processor, add health check endpoint'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

print("\n=== Pushing to GitHub ===")
result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
    if '403' in result.stderr or 'denied' in result.stderr.lower():
        print("\n⚠️  Authentication failed. Please check your GitHub token.")
    elif 'nothing to commit' in result.stdout.lower():
        print("\n✓ Everything is already up to date!")
    else:
        print("\n⚠️  Push may have failed. Check the errors above.")

print("\n=== Final Status ===")
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(result.stdout)


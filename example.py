"""Example usage of the face recognition system."""
import os
from database import Database
from processor import FaceRecognitionProcessor
from config import Config

def example_build_watchlist():
    """Example: Build watchlist from photos."""
    print("=== Building Watchlist ===")
    
    # Initialize database
    db = Database()
    
    # Initialize processor
    processor = FaceRecognitionProcessor(db)
    
    # Build watchlist from photos directory
    photos_dir = "./photos"  # Change this to your photos directory
    if os.path.exists(photos_dir):
        count = processor.build_watchlist(photos_dir)
        print(f"✓ Added {count} faces to watchlist")
    else:
        print(f"Photos directory '{photos_dir}' not found. Please create it and add photos.")

def example_process_image():
    """Example: Process a single image."""
    print("\n=== Processing Image ===")
    
    # Initialize database
    db = Database()
    
    # Initialize processor
    processor = FaceRecognitionProcessor(db)
    
    # Process image
    image_path = "./test.jpg"  # Change this to your test image
    if os.path.exists(image_path):
        results = processor.process_image(image_path)
        print(f"✓ Detected {len(results)} faces")
        for i, result in enumerate(results):
            if result['matched']:
                print(f"  Face {i+1}: MATCHED - {result['person_name']} (similarity: {result['similarity']:.3f})")
            else:
                print(f"  Face {i+1}: No match")
    else:
        print(f"Test image '{image_path}' not found.")

def example_process_video():
    """Example: Process a video file."""
    print("\n=== Processing Video ===")
    
    # Initialize database
    db = Database()
    
    # Initialize processor
    processor = FaceRecognitionProcessor(db)
    
    # Process video
    video_path = "./demo.mp4"  # Change this to your video file
    if os.path.exists(video_path):
        results = processor.process_video(video_path, output_file="results.json", fps=5)
        print(f"✓ Processed {len(results)} detections")
        print(f"✓ Results saved to results.json")
    else:
        print(f"Video file '{video_path}' not found.")

if __name__ == "__main__":
    print("Face Recognition System - Examples")
    print("=" * 50)
    
    # Run examples
    example_build_watchlist()
    example_process_image()
    example_process_video()
    
    print("\n" + "=" * 50)
    print("Done! Check the results.")


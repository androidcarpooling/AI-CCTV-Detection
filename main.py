"""Main entry point for face recognition system."""
import argparse
import os
import sys
from database import Database
from processor import FaceRecognitionProcessor
from dashboard import run_dashboard
from config import Config

def build_watchlist(args):
    """Build watchlist from photos directory."""
    print(f"Building watchlist from {args.photos_dir}...")
    
    # Initialize database
    db = Database()
    
    # Initialize processor
    processor = FaceRecognitionProcessor(db, similarity_threshold=args.threshold)
    
    # Build watchlist
    count = processor.build_watchlist(args.photos_dir, person_id_prefix=args.prefix)
    
    print(f"✓ Added {count} faces to watchlist")
    print(f"✓ Database: {args.output_db}")

def process_video(args):
    """Process video file."""
    print(f"Processing video: {args.video}...")
    
    # Initialize database
    db = Database(db_type=args.db_type, connection_string=args.db_url)
    
    # Initialize processor
    processor = FaceRecognitionProcessor(db, similarity_threshold=args.threshold)
    
    # Process video
    results = processor.process_video(args.video, output_file=args.output, fps=args.fps)
    
    print(f"✓ Processed {len(results)} detections")
    if args.output:
        print(f"✓ Results saved to {args.output}")

def process_rtsp(args):
    """Process RTSP stream."""
    print(f"Processing RTSP stream: {args.rtsp_url}...")
    print("Press Ctrl+C to stop")
    
    # Initialize database
    db = Database(db_type=args.db_type, connection_string=args.db_url)
    
    # Initialize processor
    processor = FaceRecognitionProcessor(db, similarity_threshold=args.threshold)
    
    try:
        processor.process_rtsp(args.rtsp_url, max_frames=args.max_frames)
    except KeyboardInterrupt:
        print("\n✓ Stopped processing")

def process_image(args):
    """Process single image."""
    print(f"Processing image: {args.image}...")
    
    # Initialize database
    db = Database(db_type=args.db_type, connection_string=args.db_url)
    
    # Initialize processor
    processor = FaceRecognitionProcessor(db, similarity_threshold=args.threshold)
    
    # Process image
    results = processor.process_image(args.image, source=args.image)
    
    print(f"✓ Detected {len(results)} faces")
    for i, result in enumerate(results):
        if result['matched']:
            print(f"  Face {i+1}: MATCHED - {result['person_name']} (similarity: {result['similarity']:.3f})")
        else:
            print(f"  Face {i+1}: No match (similarity: {result.get('similarity', 0):.3f})")

def dashboard(args):
    """Start web dashboard."""
    print(f"Starting dashboard on port {args.port}...")
    
    # Initialize database
    db = Database(db_type=args.db_type, connection_string=args.db_url)
    
    # Initialize event handler
    from event_handler import EventHandler
    events = EventHandler()
    
    # Run dashboard
    run_dashboard(port=args.port, db=db, events=events)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Face Recognition System')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Build watchlist command
    parser_build = subparsers.add_parser('build-watchlist', help='Build watchlist from photos')
    parser_build.add_argument('--photos-dir', required=True, help='Directory containing photos')
    parser_build.add_argument('--output-db', default='watchlist.db', help='Output database file')
    parser_build.add_argument('--prefix', default='person', help='Person ID prefix')
    parser_build.add_argument('--threshold', type=float, default=Config.SIMILARITY_THRESHOLD, help='Similarity threshold')
    
    # Process video command
    parser_video = subparsers.add_parser('process-video', help='Process video file')
    parser_video.add_argument('--video', required=True, help='Video file path')
    parser_video.add_argument('--watchlist', default='watchlist.db', help='Watchlist database')
    parser_video.add_argument('--output', help='Output JSON file')
    parser_video.add_argument('--fps', type=int, default=1, help='Process every Nth frame')
    parser_video.add_argument('--threshold', type=float, default=Config.SIMILARITY_THRESHOLD, help='Similarity threshold')
    parser_video.add_argument('--db-type', default='sqlite', help='Database type')
    parser_video.add_argument('--db-url', help='Database connection URL')
    
    # Process RTSP command
    parser_rtsp = subparsers.add_parser('process-rtsp', help='Process RTSP stream')
    parser_rtsp.add_argument('--rtsp-url', required=True, help='RTSP stream URL')
    parser_rtsp.add_argument('--watchlist', default='watchlist.db', help='Watchlist database')
    parser_rtsp.add_argument('--max-frames', type=int, help='Maximum frames to process')
    parser_rtsp.add_argument('--threshold', type=float, default=Config.SIMILARITY_THRESHOLD, help='Similarity threshold')
    parser_rtsp.add_argument('--db-type', default='sqlite', help='Database type')
    parser_rtsp.add_argument('--db-url', help='Database connection URL')
    
    # Process image command
    parser_image = subparsers.add_parser('process-image', help='Process single image')
    parser_image.add_argument('--image', required=True, help='Image file path')
    parser_image.add_argument('--watchlist', default='watchlist.db', help='Watchlist database')
    parser_image.add_argument('--threshold', type=float, default=Config.SIMILARITY_THRESHOLD, help='Similarity threshold')
    parser_image.add_argument('--db-type', default='sqlite', help='Database type')
    parser_image.add_argument('--db-url', help='Database connection URL')
    
    # Dashboard command
    parser_dashboard = subparsers.add_parser('dashboard', help='Start web dashboard')
    parser_dashboard.add_argument('--port', type=int, default=5000, help='Port number')
    parser_dashboard.add_argument('--watchlist', default='watchlist.db', help='Watchlist database')
    parser_dashboard.add_argument('--db-type', default='sqlite', help='Database type')
    parser_dashboard.add_argument('--db-url', help='Database connection URL')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'build-watchlist':
        Config.DATABASE_URL = args.output_db
        build_watchlist(args)
    elif args.command == 'process-video':
        if hasattr(args, 'db_url') and args.db_url:
            Config.DATABASE_URL = args.db_url
        elif hasattr(args, 'watchlist'):
            Config.DATABASE_URL = args.watchlist
        process_video(args)
    elif args.command == 'process-rtsp':
        if hasattr(args, 'db_url') and args.db_url:
            Config.DATABASE_URL = args.db_url
        elif hasattr(args, 'watchlist'):
            Config.DATABASE_URL = args.watchlist
        process_rtsp(args)
    elif args.command == 'process-image':
        if hasattr(args, 'db_url') and args.db_url:
            Config.DATABASE_URL = args.db_url
        elif hasattr(args, 'watchlist'):
            Config.DATABASE_URL = args.watchlist
        process_image(args)
    elif args.command == 'dashboard':
        if hasattr(args, 'db_url') and args.db_url:
            Config.DATABASE_URL = args.db_url
        elif hasattr(args, 'watchlist'):
            Config.DATABASE_URL = args.watchlist
        dashboard(args)

if __name__ == '__main__':
    main()


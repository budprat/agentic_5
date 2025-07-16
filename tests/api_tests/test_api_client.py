#!/usr/bin/env python3
"""Interactive client for testing the Video Generation API."""

import requests
import json
import time
import sys
from datetime import datetime


class VideoGenerationClient:
    """Client for Video Generation API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate_video(self, content, platforms=None, style="educational", tone="professional"):
        """Submit video generation request."""
        if platforms is None:
            platforms = ["youtube"]
        
        request_data = {
            "content": content,
            "platforms": platforms,
            "style": style,
            "tone": tone,
            "duration_preferences": {
                "youtube": 300,
                "tiktok": 60,
                "instagram_reels": 30
            }
        }
        
        print("\nSubmitting request:")
        print(json.dumps(request_data, indent=2))
        
        response = self.session.post(f"{self.base_url}/generate", json=request_data)
        response.raise_for_status()
        
        return response.json()
    
    def check_status(self, job_id):
        """Check job status."""
        response = self.session.get(f"{self.base_url}/jobs/{job_id}/status")
        response.raise_for_status()
        return response.json()
    
    def get_content(self, job_id):
        """Get generated content."""
        response = self.session.get(f"{self.base_url}/jobs/{job_id}/content")
        if response.status_code == 202:
            return None  # Still processing
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, job_id, timeout=60):
        """Wait for job to complete with progress updates."""
        start_time = time.time()
        last_progress = -1
        
        print(f"\nWaiting for job {job_id} to complete...")
        print("Progress: ", end="", flush=True)
        
        while time.time() - start_time < timeout:
            status = self.check_status(job_id)
            
            # Update progress bar
            progress = status["progress"]
            if progress > last_progress:
                print(f"\rProgress: [{'=' * (progress // 5)}{' ' * (20 - progress // 5)}] {progress}% - {status['status']}", end="", flush=True)
                last_progress = progress
            
            if status["status"] == "completed":
                print("\n✓ Generation completed!")
                return True
            
            time.sleep(1)
        
        print("\n✗ Timeout waiting for completion")
        return False


def interactive_test():
    """Run interactive test."""
    import argparse
    parser = argparse.ArgumentParser(description='Video Generation API Client')
    parser.add_argument('--port', type=int, default=8000, help='API server port (default: 8000)')
    args = parser.parse_args()
    
    client = VideoGenerationClient(f"http://localhost:{args.port}")
    
    print("=" * 80)
    print("Video Generation API - Interactive Client")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{client.base_url}/health")
        response.raise_for_status()
        print("✓ API server is running")
    except Exception as e:
        print(f"✗ Cannot connect to API server at {client.base_url}")
        print(f"  Error: {e}")
        print("\nPlease start the server first:")
        print("  python3 test_api_server.py")
        return
    
    while True:
        print("\n" + "-" * 40)
        print("1. Generate new video")
        print("2. Check job status")
        print("3. Get generated content")
        print("4. Run full demo")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ")
        
        if choice == "1":
            # Get input
            content = input("\nContent/Topic: ") or "Python async/await explained"
            platform = input("Platform (youtube/tiktok/instagram_reels): ") or "youtube"
            style = input("Style (educational/entertaining/promotional): ") or "educational"
            tone = input("Tone (professional/casual/humorous): ") or "professional"
            
            try:
                result = client.generate_video(content, [platform], style, tone)
                print(f"\n✓ Job created: {result['job_id']}")
                print(f"  Status URL: {result['status_url']}")
                
                # Ask if user wants to wait
                if input("\nWait for completion? (y/n): ").lower() == 'y':
                    if client.wait_for_completion(result['job_id']):
                        content = client.get_content(result['job_id'])
                        print("\nGenerated Content:")
                        print(json.dumps(content['result'], indent=2))
                        
            except Exception as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "2":
            job_id = input("\nJob ID: ")
            try:
                status = client.check_status(job_id)
                print(f"\nStatus: {status['status']}")
                print(f"Progress: {status['progress']}%")
                print(f"Created: {status['created_at']}")
                if status.get('completed_at'):
                    print(f"Completed: {status['completed_at']}")
            except Exception as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "3":
            job_id = input("\nJob ID: ")
            try:
                content = client.get_content(job_id)
                if content:
                    print("\nGenerated Content:")
                    print(json.dumps(content['result'], indent=2))
                else:
                    print("\n⚠️  Job still processing")
            except Exception as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "4":
            # Run full demo
            print("\n" + "=" * 40)
            print("FULL DEMO - Python Tutorial Video")
            print("=" * 40)
            
            try:
                # Submit request
                result = client.generate_video(
                    "Python decorators explained with examples",
                    ["youtube", "tiktok"],
                    "educational",
                    "casual"
                )
                
                job_id = result['job_id']
                print(f"\n✓ Job created: {job_id}")
                
                # Wait for completion
                if client.wait_for_completion(job_id, timeout=30):
                    # Get result
                    content = client.get_content(job_id)
                    result = content['result']
                    
                    print("\n" + "=" * 40)
                    print("GENERATION RESULTS")
                    print("=" * 40)
                    
                    # Script
                    print("\n📝 SCRIPT")
                    print(f"Content: {result['script']['content']}")
                    print(f"Duration: {result['script']['duration']}s")
                    print(f"Style: {result['script']['style']}")
                    print("\nSections:")
                    for section in result['script']['sections']:
                        print(f"  - {section['title']}: {section['duration']}s")
                    
                    # Storyboard
                    print("\n🎬 STORYBOARD")
                    print(f"Total scenes: {len(result['storyboard']['scenes'])}")
                    print(f"Visual style: {result['storyboard']['visual_style']}")
                    print("Scenes:")
                    for scene in result['storyboard']['scenes']:
                        print(f"  - Scene {scene['id']}: {scene['type']} ({scene['duration']}s)")
                    
                    # Quality
                    print("\n✅ QUALITY SCORES")
                    for metric, score in result['quality_scores'].items():
                        print(f"  - {metric}: {score:.2f}")
                    
                    # Platform optimization
                    print("\n📱 PLATFORM OPTIMIZATION")
                    for platform, config in result['platforms'].items():
                        print(f"\n{platform.upper()}:")
                        if platform == "youtube":
                            print(f"  - Duration: {config['duration']}s")
                            print(f"  - Format: {config['format']}")
                        elif platform == "tiktok" and 'clips' in config:
                            print(f"  - Format: {config['format']}")
                            print("  - Suggested clips:")
                            for clip in config['clips']:
                                print(f"    • {clip['start']}-{clip['end']}s: {clip['hook']}")
                
            except Exception as e:
                print(f"\n✗ Demo error: {e}")
        
        elif choice == "5":
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice")


if __name__ == "__main__":
    interactive_test()
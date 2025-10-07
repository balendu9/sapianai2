#!/usr/bin/env python3
"""
Start Celery worker and beat scheduler for Sapien AI-Quest
"""

import os
import sys
from celery import Celery
from app.core.config import settings

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def start_celery_worker():
    """Start Celery worker"""
    from app.celery_app import celery_app
    
    print("🚀 Starting Celery worker...")
    print(f"Redis URL: {settings.REDIS_URL}")
    print("Tasks: daily_ai_messages, check_and_end_expired_quests")
    
    # Start worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--queues=default'
    ])

def start_celery_beat():
    """Start Celery beat scheduler"""
    from app.celery_app import celery_app
    
    print("⏰ Starting Celery beat scheduler...")
    print("Scheduled tasks:")
    print("  - Daily AI messages: 2 PM UTC daily")
    print("  - Expired quest check: Every 5 minutes")
    
    # Start beat scheduler
    celery_app.start(['beat', '--loglevel=info'])

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Start Celery services')
    parser.add_argument('service', choices=['worker', 'beat'], 
                       help='Service to start: worker or beat')
    
    args = parser.parse_args()
    
    if args.service == 'worker':
        start_celery_worker()
    elif args.service == 'beat':
        start_celery_beat()

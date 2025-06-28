"""BrightData results caching system."""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class BrightDataCache:
    """Cache for BrightData API results to avoid repeated calls."""
    
    def __init__(self, cache_dir: str = "cache/brightdata"):
        self.cache_dir = cache_dir
        self.cache_ttl = timedelta(minutes=15)  # Cache for 15 minutes
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_key(self, keyword: str, date: str = "Today", sort_by: str = "Hot") -> str:
        """Generate cache key from search parameters."""
        return f"{keyword}_{date}_{sort_by}".lower().replace(" ", "_")
        
    def _get_cache_file(self, cache_key: str) -> str:
        """Get cache file path."""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
        
    async def get(self, keyword: str, date: str = "Today", sort_by: str = "Hot") -> Optional[Dict[str, Any]]:
        """Get cached results if available and not expired."""
        cache_key = self._get_cache_key(keyword, date, sort_by)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cached = self.memory_cache[cache_key]
            if self._is_valid(cached):
                logger.info(f"Cache hit (memory) for {keyword}")
                return cached['data']
                
        # Check file cache
        cache_file = self._get_cache_file(cache_key)
        if os.path.exists(cache_file):
            try:
                # Use synchronous file operations to avoid cancellation issues
                with open(cache_file, 'r') as f:
                    content = f.read()
                    cached = json.loads(content)
                    
                if self._is_valid(cached):
                    # Load into memory cache
                    self.memory_cache[cache_key] = cached
                    logger.info(f"Cache hit (file) for {keyword}")
                    return cached['data']
                else:
                    # Remove expired cache
                    os.remove(cache_file)
                    
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
                
        logger.info(f"Cache miss for {keyword}")
        return None
        
    async def set(self, keyword: str, data: Dict[str, Any], date: str = "Today", sort_by: str = "Hot"):
        """Cache the results."""
        cache_key = self._get_cache_key(keyword, date, sort_by)
        cache_file = self._get_cache_file(cache_key)
        
        cache_entry = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'keyword': keyword,
            'date': date,
            'sort_by': sort_by
        }
        
        # Save to memory cache
        self.memory_cache[cache_key] = cache_entry
        
        # Save to file cache
        try:
            # Use synchronous file operations to avoid cancellation issues
            with open(cache_file, 'w') as f:
                f.write(json.dumps(cache_entry, indent=2))
            logger.info(f"Cached results for {keyword}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            
    def _is_valid(self, cached: Dict[str, Any]) -> bool:
        """Check if cached data is still valid."""
        try:
            cached_time = datetime.fromisoformat(cached['timestamp'])
            return datetime.now() - cached_time < self.cache_ttl
        except:
            return False
            
    async def clear_expired(self):
        """Clear expired cache entries."""
        # Clear memory cache
        expired_keys = []
        for key, cached in self.memory_cache.items():
            if not self._is_valid(cached):
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.memory_cache[key]
            
        # Clear file cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    async with aiofiles.open(file_path, 'r') as f:
                        content = await f.read()
                        cached = json.loads(content)
                        
                    if not self._is_valid(cached):
                        os.remove(file_path)
                        logger.info(f"Removed expired cache: {filename}")
                        
                except Exception as e:
                    logger.error(f"Error cleaning cache {filename}: {e}")


class BrightDataParser:
    """Parser for BrightData Reddit results."""
    
    @staticmethod
    def parse_reddit_posts(raw_data: Any) -> Dict[str, Any]:
        """Parse raw BrightData response into structured format."""
        try:
            posts = []
            
            # Handle NDJSON format (newline-delimited JSON)
            if isinstance(raw_data, str):
                lines = raw_data.strip().split('\n')
                items = []
                for line in lines:
                    if line.strip():
                        try:
                            item = json.loads(line)
                            items.append(item)
                        except json.JSONDecodeError:
                            continue
            # Handle regular JSON formats
            elif isinstance(raw_data, dict):
                if 'data' in raw_data:
                    # Results are ready
                    items = raw_data.get('data', [])
                elif 'items' in raw_data:
                    items = raw_data.get('items', [])
                else:
                    # Might be snapshot response
                    items = []
            else:
                items = []
                
            for item in items:
                # Parse each Reddit post - handle BrightData format
                post = {
                    'title': item.get('title', ''),
                    'text': item.get('description', item.get('selftext', item.get('text', ''))),
                    'subreddit': item.get('community_name', item.get('subreddit', '')),
                    'author': item.get('user_posted', item.get('author', '')),
                    'upvotes': int(item.get('num_upvotes', item.get('score', item.get('upvotes', 0)))),
                    'num_comments': int(item.get('num_comments', 0)),
                    'created_at': item.get('date_posted', item.get('created_utc', item.get('created_at', ''))),
                    'url': item.get('url', ''),
                    'permalink': item.get('url', item.get('permalink', '')),
                    'awards': item.get('total_awards_received', 0),
                    'upvote_ratio': float(item.get('upvote_ratio', 0.5)),
                    'is_video': bool(item.get('videos', item.get('is_video', False))),
                    'flair': item.get('tag', item.get('link_flair_text', ''))
                }
                
                # Calculate engagement score
                post['engagement_score'] = (
                    post['upvotes'] + 
                    post['num_comments'] * 2 + 
                    post['awards'] * 10
                )
                
                posts.append(post)
                
            # Sort by engagement
            posts.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            return {
                'posts': posts,
                'total_posts': len(posts),
                'metadata': {
                    'source': 'BrightData Reddit API',
                    'parsed_at': datetime.now().isoformat(),
                    'snapshot_id': raw_data.get('snapshot_id', '') if isinstance(raw_data, dict) else ''
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing BrightData response: {e}")
            return {
                'posts': [],
                'total_posts': 0,
                'error': str(e),
                'metadata': {
                    'source': 'BrightData Reddit API',
                    'parsed_at': datetime.now().isoformat()
                }
            }
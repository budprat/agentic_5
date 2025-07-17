"""
ABOUTME: Multi-source trend detection system for LinkedIn content intelligence
ABOUTME: Scrapes trends from LinkedIn, Google, Reddit, Twitter/X, and industry news sources
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum
import re
import time
import sqlite3
from pathlib import Path
import hashlib
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendSource(Enum):
    LINKEDIN_NEWS = "linkedin_news"
    LINKEDIN_PULSE = "linkedin_pulse"
    HASHTAG_VELOCITY = "hashtag_velocity"
    INFLUENCER_PATTERNS = "influencer_patterns"
    GOOGLE_TRENDS = "google_trends"
    REDDIT_BUSINESS = "reddit_business"
    TWITTER_BUSINESS = "twitter_business"
    INDUSTRY_NEWS = "industry_news"

@dataclass
class TrendData:
    source: TrendSource
    topic: str
    trend_score: float
    velocity: float
    opportunity_rating: float
    keywords: List[str]
    related_content: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class TrendAnalysis:
    trend_id: str
    topic: str
    combined_score: float
    source_breakdown: Dict[TrendSource, float]
    velocity_trend: str  # "rising", "stable", "declining"
    opportunity_rating: float
    keyword_clusters: List[str]
    content_recommendations: List[str]
    competition_level: str
    estimated_reach: int
    confidence_score: float
    last_updated: datetime

class MultiSourceTrendScraper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = Path(config.get('db_path', 'trend_intelligence.db'))
        self.source_weights = {
            TrendSource.LINKEDIN_NEWS: 0.30,
            TrendSource.LINKEDIN_PULSE: 0.20,
            TrendSource.HASHTAG_VELOCITY: 0.15,
            TrendSource.INFLUENCER_PATTERNS: 0.10,
            TrendSource.GOOGLE_TRENDS: 0.10,
            TrendSource.REDDIT_BUSINESS: 0.05,
            TrendSource.TWITTER_BUSINESS: 0.05,
            TrendSource.INDUSTRY_NEWS: 0.05
        }
        self.trend_cache = {}
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for trend tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trends (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    combined_score REAL NOT NULL,
                    source_breakdown TEXT NOT NULL,
                    velocity_trend TEXT NOT NULL,
                    opportunity_rating REAL NOT NULL,
                    keyword_clusters TEXT NOT NULL,
                    content_recommendations TEXT NOT NULL,
                    competition_level TEXT NOT NULL,
                    estimated_reach INTEGER NOT NULL,
                    confidence_score REAL NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trend_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trend_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    trend_score REAL NOT NULL,
                    velocity REAL NOT NULL,
                    opportunity_rating REAL NOT NULL,
                    keywords TEXT NOT NULL,
                    related_content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metadata TEXT NOT NULL,
                    FOREIGN KEY (trend_id) REFERENCES trends(id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trend_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trend_id TEXT NOT NULL,
                    score_history TEXT NOT NULL,
                    velocity_history TEXT NOT NULL,
                    recorded_at TIMESTAMP NOT NULL
                )
            ''')
    
    async def scrape_all_sources(self) -> List[TrendAnalysis]:
        """Scrape trends from all configured sources"""
        logger.info("Starting multi-source trend scraping...")
        
        # Create tasks for parallel scraping
        tasks = [
            self._scrape_linkedin_news(),
            self._scrape_linkedin_pulse(),
            self._scrape_hashtag_velocity(),
            self._scrape_influencer_patterns(),
            self._scrape_google_trends(),
            self._scrape_reddit_business(),
            self._scrape_twitter_business(),
            self._scrape_industry_news()
        ]
        
        # Execute all scraping tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_trend_data = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping source {list(TrendSource)[i]}: {result}")
                continue
            all_trend_data.extend(result)
        
        # Analyze and combine trends
        trend_analyses = self._analyze_and_combine_trends(all_trend_data)
        
        # Store results
        self._store_trend_analyses(trend_analyses)
        
        logger.info(f"Completed trend scraping. Found {len(trend_analyses)} trending topics.")
        
        return trend_analyses
    
    async def _scrape_linkedin_news(self) -> List[TrendData]:
        """Scrape LinkedIn News trending topics"""
        logger.info("Scraping LinkedIn News...")
        
        # Simulate LinkedIn News scraping (in production, use actual API/scraping)
        mock_news_data = [
            {
                "topic": "AI in Business Automation",
                "trend_score": 85.5,
                "velocity": 12.3,
                "keywords": ["AI", "automation", "business efficiency", "machine learning"],
                "related_content": ["AI Implementation Guide", "Automation ROI Calculator"],
                "metadata": {"source_url": "https://news.linkedin.com/ai-business", "engagement": 15000}
            },
            {
                "topic": "Remote Work Future",
                "trend_score": 78.2,
                "velocity": 8.7,
                "keywords": ["remote work", "hybrid work", "workplace flexibility", "productivity"],
                "related_content": ["Remote Work Best Practices", "Hybrid Office Models"],
                "metadata": {"source_url": "https://news.linkedin.com/remote-work", "engagement": 12000}
            },
            {
                "topic": "Sustainability in Business",
                "trend_score": 72.1,
                "velocity": 15.6,
                "keywords": ["sustainability", "ESG", "green business", "climate change"],
                "related_content": ["Sustainable Business Practices", "ESG Reporting"],
                "metadata": {"source_url": "https://news.linkedin.com/sustainability", "engagement": 9500}
            }
        ]
        
        trend_data = []
        for item in mock_news_data:
            trend = TrendData(
                source=TrendSource.LINKEDIN_NEWS,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    async def _scrape_linkedin_pulse(self) -> List[TrendData]:
        """Scrape LinkedIn Pulse trending articles"""
        logger.info("Scraping LinkedIn Pulse...")
        
        # Simulate LinkedIn Pulse scraping
        mock_pulse_data = [
            {
                "topic": "Leadership in Digital Age",
                "trend_score": 68.4,
                "velocity": 9.2,
                "keywords": ["leadership", "digital transformation", "management", "innovation"],
                "related_content": ["Digital Leadership Framework", "Management 3.0"],
                "metadata": {"articles_count": 45, "avg_engagement": 3500}
            },
            {
                "topic": "Customer Experience Excellence",
                "trend_score": 64.7,
                "velocity": 7.8,
                "keywords": ["customer experience", "CX", "customer service", "satisfaction"],
                "related_content": ["CX Strategy Guide", "Customer Journey Mapping"],
                "metadata": {"articles_count": 38, "avg_engagement": 2800}
            },
            {
                "topic": "Data-Driven Decision Making",
                "trend_score": 71.3,
                "velocity": 11.5,
                "keywords": ["data analytics", "business intelligence", "decision making", "insights"],
                "related_content": ["Data Analytics for Business", "BI Dashboard Examples"],
                "metadata": {"articles_count": 52, "avg_engagement": 4200}
            }
        ]
        
        trend_data = []
        for item in mock_pulse_data:
            trend = TrendData(
                source=TrendSource.LINKEDIN_PULSE,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    async def _scrape_hashtag_velocity(self) -> List[TrendData]:
        """Track hashtag velocity on LinkedIn"""
        logger.info("Tracking hashtag velocity...")
        
        # Simulate hashtag velocity tracking
        mock_hashtag_data = [
            {
                "topic": "Digital Marketing Trends",
                "trend_score": 59.8,
                "velocity": 18.4,
                "keywords": ["digitalmarketing", "marketing", "socialmedia", "content"],
                "related_content": ["#MarketingTrends2024", "#ContentStrategy"],
                "metadata": {"hashtag_growth": 184, "posts_per_hour": 45}
            },
            {
                "topic": "Workplace Wellness",
                "trend_score": 55.2,
                "velocity": 14.7,
                "keywords": ["workplacewellness", "mentalhealth", "wellness", "productivity"],
                "related_content": ["#WorkplaceWellness", "#MentalHealthAtWork"],
                "metadata": {"hashtag_growth": 147, "posts_per_hour": 32}
            },
            {
                "topic": "Entrepreneurship Tips",
                "trend_score": 62.5,
                "velocity": 16.8,
                "keywords": ["entrepreneurship", "startup", "business", "innovation"],
                "related_content": ["#StartupLife", "#EntrepreneurMindset"],
                "metadata": {"hashtag_growth": 168, "posts_per_hour": 38}
            }
        ]
        
        trend_data = []
        for item in mock_hashtag_data:
            trend = TrendData(
                source=TrendSource.HASHTAG_VELOCITY,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    async def _scrape_influencer_patterns(self) -> List[TrendData]:
        """Analyze influencer posting patterns"""
        logger.info("Analyzing influencer patterns...")
        
        # Simulate influencer pattern analysis
        mock_influencer_data = [
            {
                "topic": "AI Tools for Productivity",
                "trend_score": 74.6,
                "velocity": 13.2,
                "keywords": ["AI tools", "productivity", "automation", "efficiency"],
                "related_content": ["Top AI Tools 2024", "Productivity Hacks"],
                "metadata": {"influencer_count": 25, "avg_engagement": 5500}
            },
            {
                "topic": "Personal Branding Strategies",
                "trend_score": 67.3,
                "velocity": 10.8,
                "keywords": ["personal branding", "professional image", "networking", "career"],
                "related_content": ["Personal Brand Framework", "LinkedIn Optimization"],
                "metadata": {"influencer_count": 18, "avg_engagement": 4200}
            }
        ]
        
        trend_data = []
        for item in mock_influencer_data:
            trend = TrendData(
                source=TrendSource.INFLUENCER_PATTERNS,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    async def _scrape_google_trends(self) -> List[TrendData]:
        """Scrape Google Trends data"""
        logger.info("Scraping Google Trends...")
        
        # Simulate Google Trends scraping
        mock_google_data = [
            {
                "topic": "Artificial Intelligence Business",
                "trend_score": 82.1,
                "velocity": 14.5,
                "keywords": ["AI business", "machine learning", "automation", "technology"],
                "related_content": ["AI in Business", "Machine Learning Applications"],
                "metadata": {"search_volume": 125000, "growth_rate": 145}
            },
            {
                "topic": "Remote Work Tools",
                "trend_score": 69.8,
                "velocity": 8.9,
                "keywords": ["remote work", "collaboration tools", "productivity", "software"],
                "related_content": ["Remote Work Solutions", "Collaboration Platforms"],
                "metadata": {"search_volume": 98000, "growth_rate": 89}
            }
        ]
        
        trend_data = []
        for item in mock_google_data:
            trend = TrendData(
                source=TrendSource.GOOGLE_TRENDS,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    async def _scrape_reddit_business(self) -> List[TrendData]:
        """Scrape Reddit business-related hot topics"""
        logger.info("Scraping Reddit business topics...")
        
        # Simulate Reddit scraping
        mock_reddit_data = [
            {
                "topic": "Small Business Marketing",
                "trend_score": 45.2,
                "velocity": 6.7,
                "keywords": ["small business", "marketing", "local business", "advertising"],
                "related_content": ["Small Business Tips", "Local Marketing Strategies"],
                "metadata": {"subreddit": "r/smallbusiness", "upvotes": 2400}
            },
            {
                "topic": "Freelancing Success",
                "trend_score": 41.8,
                "velocity": 5.9,
                "keywords": ["freelancing", "gig economy", "remote work", "independence"],
                "related_content": ["Freelance Best Practices", "Gig Economy Guide"],
                "metadata": {"subreddit": "r/freelance", "upvotes": 1900}
            }
        ]
        
        trend_data = []
        for item in mock_reddit_data:
            trend = TrendData(
                source=TrendSource.REDDIT_BUSINESS,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    async def _scrape_twitter_business(self) -> List[TrendData]:
        """Scrape Twitter/X business trending topics"""
        logger.info("Scraping Twitter/X business topics...")
        
        # Simulate Twitter scraping
        mock_twitter_data = [
            {
                "topic": "Tech Industry News",
                "trend_score": 56.4,
                "velocity": 9.3,
                "keywords": ["tech news", "technology", "innovation", "startups"],
                "related_content": ["Tech Industry Updates", "Startup News"],
                "metadata": {"tweet_volume": 15000, "trending_duration": 4}
            },
            {
                "topic": "Business Strategy",
                "trend_score": 52.1,
                "velocity": 7.2,
                "keywords": ["business strategy", "corporate", "planning", "growth"],
                "related_content": ["Strategy Frameworks", "Business Planning"],
                "metadata": {"tweet_volume": 12000, "trending_duration": 3}
            }
        ]
        
        trend_data = []
        for item in mock_twitter_data:
            trend = TrendData(
                source=TrendSource.TWITTER_BUSINESS,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    async def _scrape_industry_news(self) -> List[TrendData]:
        """Scrape industry news aggregators"""
        logger.info("Scraping industry news...")
        
        # Simulate industry news scraping
        mock_news_data = [
            {
                "topic": "Cybersecurity Trends",
                "trend_score": 66.7,
                "velocity": 11.4,
                "keywords": ["cybersecurity", "data protection", "security", "privacy"],
                "related_content": ["Cybersecurity Best Practices", "Data Protection Guide"],
                "metadata": {"news_sources": 12, "article_count": 85}
            },
            {
                "topic": "Financial Technology",
                "trend_score": 63.9,
                "velocity": 10.2,
                "keywords": ["fintech", "financial technology", "digital banking", "payments"],
                "related_content": ["FinTech Innovation", "Digital Banking Trends"],
                "metadata": {"news_sources": 8, "article_count": 67}
            }
        ]
        
        trend_data = []
        for item in mock_news_data:
            trend = TrendData(
                source=TrendSource.INDUSTRY_NEWS,
                topic=item["topic"],
                trend_score=item["trend_score"],
                velocity=item["velocity"],
                opportunity_rating=self._calculate_opportunity_rating(item["trend_score"], item["velocity"]),
                keywords=item["keywords"],
                related_content=item["related_content"],
                timestamp=datetime.now(),
                metadata=item["metadata"]
            )
            trend_data.append(trend)
        
        return trend_data
    
    def _calculate_opportunity_rating(self, trend_score: float, velocity: float) -> float:
        """Calculate opportunity rating based on trend score and velocity"""
        # Higher trend score and velocity = higher opportunity
        base_opportunity = (trend_score / 100) * 0.7
        velocity_boost = min(velocity / 20, 0.3)  # Cap velocity boost at 0.3
        return min(base_opportunity + velocity_boost, 1.0)
    
    def _analyze_and_combine_trends(self, trend_data: List[TrendData]) -> List[TrendAnalysis]:
        """Analyze and combine trends from multiple sources"""
        logger.info("Analyzing and combining trends...")
        
        # Group trends by similar topics
        topic_groups = defaultdict(list)
        for trend in trend_data:
            # Simple topic grouping based on keywords overlap
            group_key = self._find_topic_group(trend.topic, trend.keywords, topic_groups)
            topic_groups[group_key].append(trend)
        
        # Analyze each topic group
        trend_analyses = []
        for topic_group, trends in topic_groups.items():
            analysis = self._create_trend_analysis(topic_group, trends)
            trend_analyses.append(analysis)
        
        # Sort by combined score
        trend_analyses.sort(key=lambda x: x.combined_score, reverse=True)
        
        return trend_analyses
    
    def _find_topic_group(self, topic: str, keywords: List[str], existing_groups: Dict[str, List]) -> str:
        """Find appropriate topic group or create new one"""
        # Calculate similarity with existing groups
        max_similarity = 0
        best_group = None
        
        for group_key, trends in existing_groups.items():
            similarity = self._calculate_topic_similarity(topic, keywords, group_key, trends)
            if similarity > max_similarity and similarity > 0.6:  # Threshold for grouping
                max_similarity = similarity
                best_group = group_key
        
        return best_group or topic
    
    def _calculate_topic_similarity(self, topic: str, keywords: List[str], group_key: str, group_trends: List[TrendData]) -> float:
        """Calculate similarity between topic and existing group"""
        # Simple keyword overlap calculation
        all_group_keywords = set()
        for trend in group_trends:
            all_group_keywords.update(trend.keywords)
        
        keyword_overlap = len(set(keywords) & all_group_keywords)
        total_keywords = len(set(keywords) | all_group_keywords)
        
        if total_keywords == 0:
            return 0
        
        return keyword_overlap / total_keywords
    
    def _create_trend_analysis(self, topic: str, trends: List[TrendData]) -> TrendAnalysis:
        """Create comprehensive trend analysis from multiple sources"""
        # Calculate weighted combined score
        combined_score = 0
        source_breakdown = {}
        
        for trend in trends:
            weight = self.source_weights.get(trend.source, 0.05)
            combined_score += trend.trend_score * weight
            source_breakdown[trend.source] = trend.trend_score
        
        # Calculate average opportunity rating
        avg_opportunity = sum(trend.opportunity_rating for trend in trends) / len(trends)
        
        # Determine velocity trend
        velocities = [trend.velocity for trend in trends]
        avg_velocity = sum(velocities) / len(velocities)
        
        if avg_velocity > 10:
            velocity_trend = "rising"
        elif avg_velocity > 5:
            velocity_trend = "stable"
        else:
            velocity_trend = "declining"
        
        # Combine keywords
        all_keywords = set()
        all_content = []
        
        for trend in trends:
            all_keywords.update(trend.keywords)
            all_content.extend(trend.related_content)
        
        # Calculate competition level
        competition_level = self._calculate_competition_level(combined_score, len(trends))
        
        # Estimate reach
        estimated_reach = self._estimate_reach(combined_score, avg_velocity)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(trends, len(source_breakdown))
        
        # Generate content recommendations
        content_recommendations = self._generate_content_recommendations(topic, list(all_keywords))
        
        # Create trend ID
        trend_id = hashlib.md5(f"{topic}_{datetime.now().date()}".encode()).hexdigest()
        
        return TrendAnalysis(
            trend_id=trend_id,
            topic=topic,
            combined_score=combined_score,
            source_breakdown=source_breakdown,
            velocity_trend=velocity_trend,
            opportunity_rating=avg_opportunity,
            keyword_clusters=self._create_keyword_clusters(list(all_keywords)),
            content_recommendations=content_recommendations,
            competition_level=competition_level,
            estimated_reach=estimated_reach,
            confidence_score=confidence_score,
            last_updated=datetime.now()
        )
    
    def _calculate_competition_level(self, score: float, source_count: int) -> str:
        """Calculate competition level based on score and source diversity"""
        if score > 70 and source_count >= 3:
            return "high"
        elif score > 50 and source_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _estimate_reach(self, score: float, velocity: float) -> int:
        """Estimate potential reach based on score and velocity"""
        base_reach = int(score * 1000)  # Base reach proportional to score
        velocity_multiplier = 1 + (velocity / 20)  # Velocity boost
        return int(base_reach * velocity_multiplier)
    
    def _calculate_confidence_score(self, trends: List[TrendData], source_diversity: int) -> float:
        """Calculate confidence score based on data quality and diversity"""
        # Base confidence from source diversity
        diversity_score = min(source_diversity / 8, 1.0)  # Max 8 sources
        
        # Data quality score
        quality_scores = []
        for trend in trends:
            # Simple quality metric based on metadata richness
            metadata_richness = len(trend.metadata) / 5  # Assume 5 fields is good
            quality_scores.append(min(metadata_richness, 1.0))
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Combine diversity and quality
        confidence = (diversity_score * 0.6) + (avg_quality * 0.4)
        
        return min(confidence, 1.0)
    
    def _create_keyword_clusters(self, keywords: List[str]) -> List[str]:
        """Create keyword clusters from all keywords"""
        # Simple clustering by grouping related keywords
        clusters = []
        processed = set()
        
        for keyword in keywords:
            if keyword in processed:
                continue
                
            # Find related keywords
            cluster = [keyword]
            for other_keyword in keywords:
                if other_keyword != keyword and other_keyword not in processed:
                    # Simple relatedness check
                    if self._are_keywords_related(keyword, other_keyword):
                        cluster.append(other_keyword)
                        processed.add(other_keyword)
            
            if cluster:
                clusters.append(", ".join(cluster))
                processed.add(keyword)
        
        return clusters[:5]  # Return top 5 clusters
    
    def _are_keywords_related(self, keyword1: str, keyword2: str) -> bool:
        """Check if two keywords are related"""
        # Simple check for word overlap or similar themes
        words1 = set(keyword1.lower().split())
        words2 = set(keyword2.lower().split())
        
        # Check for word overlap
        if words1 & words2:
            return True
        
        # Check for semantic similarity (simplified)
        business_terms = {"business", "work", "professional", "corporate", "industry"}
        tech_terms = {"technology", "digital", "AI", "automation", "software"}
        
        if (words1 & business_terms) and (words2 & business_terms):
            return True
        if (words1 & tech_terms) and (words2 & tech_terms):
            return True
        
        return False
    
    def _generate_content_recommendations(self, topic: str, keywords: List[str]) -> List[str]:
        """Generate content recommendations based on topic and keywords"""
        recommendations = []
        
        # Template-based recommendations
        templates = [
            f"5 Key Trends in {topic}",
            f"How to Leverage {topic} for Business Growth",
            f"The Future of {topic}: Expert Predictions",
            f"{topic} Best Practices for 2024",
            f"Common Mistakes to Avoid in {topic}"
        ]
        
        recommendations.extend(templates)
        
        # Keyword-based recommendations
        for keyword in keywords[:3]:  # Use top 3 keywords
            recommendations.append(f"Complete Guide to {keyword.title()}")
            recommendations.append(f"Why {keyword.title()} Matters Now")
        
        return recommendations[:7]  # Return top 7 recommendations
    
    def _store_trend_analyses(self, trend_analyses: List[TrendAnalysis]):
        """Store trend analyses in database"""
        with sqlite3.connect(self.db_path) as conn:
            for analysis in trend_analyses:
                # Store main analysis
                conn.execute('''
                    INSERT OR REPLACE INTO trends (
                        id, topic, combined_score, source_breakdown, velocity_trend,
                        opportunity_rating, keyword_clusters, content_recommendations,
                        competition_level, estimated_reach, confidence_score, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analysis.trend_id,
                    analysis.topic,
                    analysis.combined_score,
                    json.dumps({k.name: v for k, v in analysis.source_breakdown.items()}),
                    analysis.velocity_trend,
                    analysis.opportunity_rating,
                    json.dumps(analysis.keyword_clusters),
                    json.dumps(analysis.content_recommendations),
                    analysis.competition_level,
                    analysis.estimated_reach,
                    analysis.confidence_score,
                    analysis.last_updated
                ))
    
    async def get_trending_opportunities(self, limit: int = 10) -> List[TrendAnalysis]:
        """Get top trending opportunities"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM trends
                ORDER BY combined_score DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                analysis = TrendAnalysis(
                    trend_id=row[0],
                    topic=row[1],
                    combined_score=row[2],
                    source_breakdown={TrendSource[k]: v for k, v in json.loads(row[3]).items()},
                    velocity_trend=row[4],
                    opportunity_rating=row[5],
                    keyword_clusters=json.loads(row[6]),
                    content_recommendations=json.loads(row[7]),
                    competition_level=row[8],
                    estimated_reach=row[9],
                    confidence_score=row[10],
                    last_updated=datetime.fromisoformat(row[11])
                )
                results.append(analysis)
            
            return results
    
    async def generate_trend_report(self) -> Dict[str, Any]:
        """Generate comprehensive trend report"""
        logger.info("Generating trend report...")
        
        # Get recent trends
        trends = await self.get_trending_opportunities(20)
        
        # Calculate summary statistics
        avg_score = sum(trend.combined_score for trend in trends) / len(trends) if trends else 0
        high_opportunity_count = sum(1 for trend in trends if trend.opportunity_rating > 0.7)
        rising_trends_count = sum(1 for trend in trends if trend.velocity_trend == "rising")
        
        # Identify top opportunities
        top_opportunities = trends[:5]
        
        # Generate insights
        insights = self._generate_trend_insights(trends)
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_trends_analyzed": len(trends),
                "average_trend_score": avg_score,
                "high_opportunity_trends": high_opportunity_count,
                "rising_trends": rising_trends_count,
                "data_sources_used": len(self.source_weights)
            },
            "top_opportunities": [asdict(trend) for trend in top_opportunities],
            "insights": insights,
            "source_performance": self._analyze_source_performance(trends),
            "recommended_actions": self._generate_trend_recommendations(trends)
        }
        
        # Save report
        report_path = f"/Users/mac/Agents/agentic_5/linkedin-domination/analytics-dashboards/trend_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _generate_trend_insights(self, trends: List[TrendAnalysis]) -> List[Dict[str, Any]]:
        """Generate insights from trend analysis"""
        insights = []
        
        if not trends:
            return insights
        
        # Rising trends insight
        rising_trends = [t for t in trends if t.velocity_trend == "rising"]
        if rising_trends:
            insights.append({
                "type": "rising_trends",
                "title": f"{len(rising_trends)} Rising Trends Detected",
                "description": f"Topics showing strong upward momentum: {', '.join([t.topic for t in rising_trends[:3]])}",
                "impact": "High potential for viral content and engagement"
            })
        
        # High opportunity insight
        high_opportunity = [t for t in trends if t.opportunity_rating > 0.7]
        if high_opportunity:
            insights.append({
                "type": "high_opportunity",
                "title": f"{len(high_opportunity)} High-Opportunity Topics",
                "description": f"Topics with strong opportunity scores: {', '.join([t.topic for t in high_opportunity[:3]])}",
                "impact": "Excellent potential for thought leadership content"
            })
        
        # Competition analysis
        low_competition = [t for t in trends if t.competition_level == "low"]
        if low_competition:
            insights.append({
                "type": "low_competition",
                "title": f"{len(low_competition)} Low-Competition Opportunities",
                "description": f"Topics with less competition: {', '.join([t.topic for t in low_competition[:3]])}",
                "impact": "Great opportunity to establish authority"
            })
        
        return insights
    
    def _analyze_source_performance(self, trends: List[TrendAnalysis]) -> Dict[str, Any]:
        """Analyze performance of different trend sources"""
        source_stats = defaultdict(lambda: {"count": 0, "avg_score": 0, "total_score": 0})
        
        for trend in trends:
            for source, score in trend.source_breakdown.items():
                source_stats[source.name]["count"] += 1
                source_stats[source.name]["total_score"] += score
        
        # Calculate averages
        for source, stats in source_stats.items():
            if stats["count"] > 0:
                stats["avg_score"] = stats["total_score"] / stats["count"]
        
        return dict(source_stats)
    
    def _generate_trend_recommendations(self, trends: List[TrendAnalysis]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on trends"""
        recommendations = []
        
        if not trends:
            return recommendations
        
        # Top priority recommendations
        top_trend = trends[0]
        recommendations.append({
            "priority": "High",
            "action": f"Create content series on '{top_trend.topic}'",
            "rationale": f"Highest trend score ({top_trend.combined_score:.1f}) with {top_trend.velocity_trend} velocity",
            "suggested_content": top_trend.content_recommendations[:3],
            "timeline": "This week"
        })
        
        # Rising trend recommendations
        rising_trends = [t for t in trends[:5] if t.velocity_trend == "rising"]
        if rising_trends:
            recommendations.append({
                "priority": "Medium",
                "action": f"Monitor and prepare content for rising trends",
                "rationale": f"{len(rising_trends)} trends showing strong momentum",
                "suggested_content": [f"Trend analysis: {t.topic}" for t in rising_trends[:3]],
                "timeline": "Next week"
            })
        
        # Low competition recommendations
        low_competition = [t for t in trends[:10] if t.competition_level == "low"]
        if low_competition:
            recommendations.append({
                "priority": "Medium",
                "action": f"Establish authority in low-competition areas",
                "rationale": f"{len(low_competition)} topics with minimal competition",
                "suggested_content": [f"Comprehensive guide: {t.topic}" for t in low_competition[:3]],
                "timeline": "Next 2 weeks"
            })
        
        return recommendations

# Usage example
async def main():
    config = {
        'db_path': '/Users/mac/Agents/agentic_5/linkedin-domination/data-storage/trend_intelligence.db',
        'api_keys': {
            'google_trends': 'your_google_trends_key',
            'reddit': 'your_reddit_key',
            'twitter': 'your_twitter_key'
        }
    }
    
    scraper = MultiSourceTrendScraper(config)
    
    # Scrape all sources
    trends = await scraper.scrape_all_sources()
    
    # Generate report
    report = await scraper.generate_trend_report()
    
    print(f"Trend scraping complete! Found {len(trends)} trending topics.")
    print(f"Report generated with {len(report['top_opportunities'])} top opportunities.")

if __name__ == "__main__":
    asyncio.run(main())
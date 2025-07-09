"""
Solopreneur-specific MCP tools implementation.
Extends the existing server.py with domain-specific tools.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

from mcp.server import Server
from neo4j import GraphDatabase
import arxiv
import requests

logger = logging.getLogger(__name__)

# Database paths
SOLOPRENEUR_DB = os.getenv('SOLOPRENEUR_DB', 'solopreneur.db')
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Initialize Neo4j driver
neo4j_driver = None
try:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
except Exception as e:
    logger.warning(f"Neo4j connection failed: {e}. Knowledge graph features will be disabled.")

def init_solopreneur_tools(server: Server):
    """Initialize all solopreneur-specific MCP tools."""
    
    @server.call_tool()
    def query_solopreneur_metrics(
        metric_type: str,
        user_id: str = "default",
        time_range: str = "day",
        aggregation: str = "avg"
    ) -> dict:
        """
        Query personal optimization metrics from the database.
        
        Args:
            metric_type: Type of metric ('energy', 'focus', 'productivity', 'stress')
            user_id: User identifier
            time_range: Time range ('day', 'week', 'month')
            aggregation: Aggregation method ('avg', 'max', 'min', 'sum')
        """
        logger.info(f'Query solopreneur metrics: {metric_type} for {time_range}')
        
        # Calculate date range
        end_date = datetime.now()
        if time_range == 'day':
            start_date = end_date - timedelta(days=1)
        elif time_range == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif time_range == 'month':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        try:
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = f"""
                SELECT 
                    DATE(timestamp) as date,
                    {aggregation}(value) as {aggregation}_value,
                    COUNT(*) as data_points,
                    MIN(value) as min_value,
                    MAX(value) as max_value
                FROM personal_metrics
                WHERE user_id = ? 
                    AND metric_type = ?
                    AND timestamp BETWEEN ? AND ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                """
                
                cursor.execute(query, (user_id, metric_type, start_date, end_date))
                rows = cursor.fetchall()
                
                results = {
                    'metric_type': metric_type,
                    'time_range': time_range,
                    'aggregation': aggregation,
                    'data': [dict(row) for row in rows],
                    'summary': {
                        'total_data_points': sum(row['data_points'] for row in rows),
                        'overall_avg': sum(row[f'{aggregation}_value'] * row['data_points'] for row in rows) / sum(row['data_points'] for row in rows) if rows else 0
                    }
                }
                
                return json.dumps(results)
        except Exception as e:
            logger.error(f'Error querying metrics: {e}')
            return json.dumps({'error': str(e)})
    
    @server.call_tool()
    def analyze_energy_patterns(
        user_id: str = "default",
        date: Optional[str] = None
    ) -> dict:
        """
        Analyze energy patterns to find optimal work windows.
        
        Args:
            user_id: User identifier
            date: Specific date to analyze (YYYY-MM-DD) or None for today
        """
        logger.info(f'Analyze energy patterns for user: {user_id}')
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get energy patterns for the date
                cursor.execute("""
                SELECT hour, energy_level, cognitive_capacity, optimal_task_types
                FROM energy_patterns
                WHERE user_id = ? AND date = ?
                ORDER BY hour
                """, (user_id, date))
                
                patterns = cursor.fetchall()
                
                if not patterns:
                    # Get average patterns if no data for specific date
                    cursor.execute("""
                    SELECT 
                        hour,
                        AVG(energy_level) as energy_level,
                        AVG(cognitive_capacity) as cognitive_capacity,
                        GROUP_CONCAT(DISTINCT optimal_task_types) as optimal_task_types
                    FROM energy_patterns
                    WHERE user_id = ?
                    GROUP BY hour
                    ORDER BY hour
                    """, (user_id,))
                    patterns = cursor.fetchall()
                
                # Analyze patterns
                peak_hours = []
                low_hours = []
                deep_work_windows = []
                
                for row in patterns:
                    hour_data = dict(row)
                    if hour_data['energy_level'] >= 8:
                        peak_hours.append(hour_data['hour'])
                    elif hour_data['energy_level'] <= 4:
                        low_hours.append(hour_data['hour'])
                    
                    if hour_data['cognitive_capacity'] >= 8:
                        deep_work_windows.append({
                            'hour': hour_data['hour'],
                            'capacity': hour_data['cognitive_capacity'],
                            'optimal_tasks': json.loads(hour_data['optimal_task_types']) if hour_data['optimal_task_types'] else []
                        })
                
                return json.dumps({
                    'date': date,
                    'patterns': [dict(row) for row in patterns],
                    'analysis': {
                        'peak_energy_hours': peak_hours,
                        'low_energy_hours': low_hours,
                        'deep_work_windows': deep_work_windows,
                        'recommendations': generate_schedule_recommendations(patterns)
                    }
                })
                
        except Exception as e:
            logger.error(f'Error analyzing energy patterns: {e}')
            return json.dumps({'error': str(e)})
    
    @server.call_tool()
    def query_knowledge_graph(
        query_type: str,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> dict:
        """
        Query the Neo4j knowledge graph for insights and connections.
        
        Args:
            query_type: Type of query ('connections', 'insights', 'patterns')
            domain: Domain filter ('technical', 'personal', 'learning', 'project')
            limit: Maximum number of results
        """
        logger.info(f'Query knowledge graph: {query_type} in domain: {domain}')
        
        if not neo4j_driver:
            return json.dumps({'error': 'Neo4j connection not available'})
        
        try:
            with neo4j_driver.session() as session:
                if query_type == 'connections':
                    # Find highly connected knowledge items
                    cypher = """
                    MATCH (k:KnowledgeItem)-[r:CONNECTS_TO]-(related:KnowledgeItem)
                    WHERE ($domain IS NULL OR k.domain = $domain)
                    WITH k, COUNT(DISTINCT related) as connection_count
                    RETURN k.id as id, k.title as title, k.domain as domain, 
                           k.content as content, connection_count
                    ORDER BY connection_count DESC
                    LIMIT $limit
                    """
                    
                elif query_type == 'insights':
                    # Find high-value insights
                    cypher = """
                    MATCH (k:KnowledgeItem)
                    WHERE k.item_type = 'insight' 
                        AND ($domain IS NULL OR k.domain = $domain)
                        AND k.confidence_score > 0.7
                    RETURN k.id as id, k.title as title, k.content as content,
                           k.confidence_score as confidence, k.relevance_score as relevance
                    ORDER BY k.relevance_score DESC
                    LIMIT $limit
                    """
                    
                elif query_type == 'patterns':
                    # Find recurring patterns
                    cypher = """
                    MATCH (k:KnowledgeItem)-[r:PATTERN_OF]->(source)
                    WHERE k.item_type = 'pattern'
                        AND ($domain IS NULL OR k.domain = $domain)
                    WITH k, COUNT(DISTINCT source) as occurrence_count
                    RETURN k.id as id, k.title as title, k.content as content,
                           occurrence_count, k.metadata as metadata
                    ORDER BY occurrence_count DESC
                    LIMIT $limit
                    """
                else:
                    return json.dumps({'error': f'Unknown query type: {query_type}'})
                
                result = session.run(cypher, domain=domain, limit=limit)
                records = [dict(record) for record in result]
                
                return json.dumps({
                    'query_type': query_type,
                    'domain': domain,
                    'results': records,
                    'count': len(records)
                })
                
        except Exception as e:
            logger.error(f'Neo4j query error: {e}')
            return json.dumps({'error': str(e)})
    
    @server.call_tool()
    def monitor_technical_trends(
        research_areas: List[str],
        sources: List[str] = ['arxiv', 'github'],
        limit: int = 10
    ) -> dict:
        """
        Monitor technical trends from various sources.
        
        Args:
            research_areas: List of research areas to monitor
            sources: List of sources to check
            limit: Maximum results per source
        """
        logger.info(f'Monitor technical trends: {research_areas} from {sources}')
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'research_areas': research_areas,
            'sources': {}
        }
        
        for source in sources:
            if source == 'arxiv' and 'arxiv' in sources:
                results['sources']['arxiv'] = monitor_arxiv(research_areas, limit)
            elif source == 'github' and GITHUB_TOKEN:
                results['sources']['github'] = monitor_github(research_areas, limit)
        
        # Store relevant findings in database
        store_technical_intelligence(results)
        
        return json.dumps(results)
    
    @server.call_tool()
    def optimize_task_schedule(
        tasks: List[Dict[str, Any]],
        user_id: str = "default",
        optimization_strategy: str = "energy_aware"
    ) -> dict:
        """
        Optimize task scheduling based on energy patterns and task requirements.
        
        Args:
            tasks: List of tasks with complexity and estimated duration
            user_id: User identifier
            optimization_strategy: Strategy to use ('energy_aware', 'deadline_first', 'complexity_based')
        """
        logger.info(f'Optimize task schedule with strategy: {optimization_strategy}')
        
        try:
            # Get user's energy patterns
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get average energy patterns
                cursor.execute("""
                SELECT 
                    hour,
                    AVG(energy_level) as avg_energy,
                    AVG(cognitive_capacity) as avg_cognitive
                FROM energy_patterns
                WHERE user_id = ?
                GROUP BY hour
                ORDER BY hour
                """, (user_id,))
                
                energy_patterns = {row['hour']: {
                    'energy': row['avg_energy'],
                    'cognitive': row['avg_cognitive']
                } for row in cursor.fetchall()}
            
            # Optimize based on strategy
            if optimization_strategy == 'energy_aware':
                optimized_schedule = optimize_by_energy(tasks, energy_patterns)
            elif optimization_strategy == 'deadline_first':
                optimized_schedule = optimize_by_deadline(tasks, energy_patterns)
            elif optimization_strategy == 'complexity_based':
                optimized_schedule = optimize_by_complexity(tasks, energy_patterns)
            else:
                optimized_schedule = tasks  # No optimization
            
            return json.dumps({
                'strategy': optimization_strategy,
                'original_tasks': tasks,
                'optimized_schedule': optimized_schedule,
                'recommendations': generate_schedule_insights(optimized_schedule, energy_patterns)
            })
            
        except Exception as e:
            logger.error(f'Error optimizing schedule: {e}')
            return json.dumps({'error': str(e)})
    
    @server.call_tool()
    def track_learning_progress(
        skill_name: str,
        user_id: str = "default",
        update_data: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Track and update learning progress for a skill.
        
        Args:
            skill_name: Name of the skill
            user_id: User identifier
            update_data: Optional data to update (hours, level, milestones)
        """
        logger.info(f'Track learning progress for skill: {skill_name}')
        
        try:
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if update_data:
                    # Update skill progress
                    if 'hours' in update_data:
                        cursor.execute("""
                        UPDATE skill_progress 
                        SET hours_invested = hours_invested + ?,
                            last_practice_date = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND skill_name = ?
                        """, (update_data['hours'], user_id, skill_name))
                    
                    if 'level' in update_data:
                        cursor.execute("""
                        UPDATE skill_progress 
                        SET current_level = ?
                        WHERE user_id = ? AND skill_name = ?
                        """, (update_data['level'], user_id, skill_name))
                    
                    conn.commit()
                
                # Get current progress
                cursor.execute("""
                SELECT sp.*, 
                    COUNT(ls.id) as total_sessions,
                    AVG(ls.productivity_score) as avg_productivity
                FROM skill_progress sp
                LEFT JOIN learning_sessions ls ON sp.id = ls.skill_id
                WHERE sp.user_id = ? AND sp.skill_name = ?
                GROUP BY sp.id
                """, (user_id, skill_name))
                
                progress = cursor.fetchone()
                
                if not progress:
                    # Create new skill entry
                    cursor.execute("""
                    INSERT INTO skill_progress (user_id, skill_name, current_level, target_level)
                    VALUES (?, ?, 1, 5)
                    """, (user_id, skill_name))
                    conn.commit()
                    
                    progress = cursor.execute("""
                    SELECT * FROM skill_progress 
                    WHERE user_id = ? AND skill_name = ?
                    """, (user_id, skill_name)).fetchone()
                
                # Calculate learning velocity
                learning_velocity = calculate_learning_velocity(progress)
                
                return json.dumps({
                    'skill': skill_name,
                    'progress': dict(progress),
                    'learning_velocity': learning_velocity,
                    'recommendations': generate_learning_recommendations(progress)
                })
                
        except Exception as e:
            logger.error(f'Error tracking learning progress: {e}')
            return json.dumps({'error': str(e)})
    
    @server.call_tool()
    def search_relevant_research(
        query: str,
        research_area: str,
        max_results: int = 20
    ) -> dict:
        """
        Search for relevant research papers and technical content.
        
        Args:
            query: Search query
            research_area: Specific research area
            max_results: Maximum number of results
        """
        logger.info(f'Search relevant research: {query} in {research_area}')
        
        try:
            # Search ArXiv
            arxiv_results = []
            if 'arxiv' in ['arxiv']:  # Check if ArXiv is enabled
                client = arxiv.Client()
                search = arxiv.Search(
                    query=f"{query} AND cat:{research_area}",
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                for result in client.results(search):
                    arxiv_results.append({
                        'arxiv_id': result.entry_id.split('/')[-1],
                        'title': result.title,
                        'authors': [author.name for author in result.authors],
                        'abstract': result.summary,
                        'categories': result.categories,
                        'published': result.published.isoformat(),
                        'url': result.pdf_url
                    })
            
            # Search stored technical intelligence
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT * FROM technical_intelligence
                WHERE research_area = ? 
                    AND (title LIKE ? OR summary LIKE ?)
                ORDER BY relevance_score DESC
                LIMIT ?
                """, (research_area, f'%{query}%', f'%{query}%', max_results))
                
                stored_results = [dict(row) for row in cursor.fetchall()]
            
            return json.dumps({
                'query': query,
                'research_area': research_area,
                'arxiv_results': arxiv_results,
                'stored_results': stored_results,
                'total_results': len(arxiv_results) + len(stored_results)
            })
            
        except Exception as e:
            logger.error(f'Error searching research: {e}')
            return json.dumps({'error': str(e)})
    
    @server.call_tool()
    def analyze_workflow_patterns(
        user_id: str = "default",
        time_period: int = 30
    ) -> dict:
        """
        Analyze workflow patterns to identify optimization opportunities.
        
        Args:
            user_id: User identifier
            time_period: Days to analyze
        """
        logger.info(f'Analyze workflow patterns for user: {user_id}')
        
        try:
            with sqlite3.connect(SOLOPRENEUR_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Analyze task completion patterns
                cursor.execute("""
                SELECT 
                    task_type,
                    AVG(actual_hours / NULLIF(estimated_hours, 0)) as estimation_accuracy,
                    AVG(actual_hours) as avg_duration,
                    COUNT(*) as task_count,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count
                FROM project_tasks
                WHERE assigned_date >= date('now', '-{} days')
                GROUP BY task_type
                """.format(time_period))
                
                task_patterns = [dict(row) for row in cursor.fetchall()]
                
                # Analyze productivity by time of day
                cursor.execute("""
                SELECT 
                    strftime('%H', start_time) as hour,
                    AVG(productivity_score) as avg_productivity,
                    AVG(focus_score) as avg_focus,
                    COUNT(*) as session_count
                FROM focus_sessions
                WHERE user_id = ? 
                    AND start_time >= date('now', '-{} days')
                GROUP BY hour
                ORDER BY hour
                """.format(time_period), (user_id,))
                
                productivity_patterns = [dict(row) for row in cursor.fetchall()]
                
                # Identify optimization opportunities
                optimizations = identify_workflow_optimizations(task_patterns, productivity_patterns)
                
                return json.dumps({
                    'analysis_period_days': time_period,
                    'task_patterns': task_patterns,
                    'productivity_patterns': productivity_patterns,
                    'optimization_opportunities': optimizations
                })
                
        except Exception as e:
            logger.error(f'Error analyzing workflow: {e}')
            return json.dumps({'error': str(e)})


# Helper functions

def monitor_arxiv(research_areas: List[str], limit: int) -> List[Dict]:
    """Monitor ArXiv for relevant papers."""
    results = []
    client = arxiv.Client()
    
    for area in research_areas:
        search = arxiv.Search(
            query=area,
            max_results=limit,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        for result in client.results(search):
            relevance = calculate_relevance_score(result, area)
            results.append({
                'source': 'arxiv',
                'arxiv_id': result.entry_id.split('/')[-1],
                'title': result.title,
                'authors': [author.name for author in result.authors][:3],  # First 3 authors
                'abstract': result.summary[:500],  # First 500 chars
                'relevance_score': relevance,
                'published_date': result.published.isoformat(),
                'url': result.pdf_url,
                'research_area': area
            })
    
    return sorted(results, key=lambda x: x['relevance_score'], reverse=True)[:limit]

def monitor_github(research_areas: List[str], limit: int) -> List[Dict]:
    """Monitor GitHub for relevant repositories."""
    results = []
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    
    for area in research_areas:
        try:
            # Search repositories
            response = requests.get(
                'https://api.github.com/search/repositories',
                params={
                    'q': f'{area} language:python stars:>100',
                    'sort': 'updated',
                    'order': 'desc',
                    'per_page': limit
                },
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                for repo in data.get('items', []):
                    results.append({
                        'source': 'github',
                        'github_id': repo['id'],
                        'full_name': repo['full_name'],
                        'description': repo['description'],
                        'stars': repo['stargazers_count'],
                        'language': repo['language'],
                        'updated_at': repo['updated_at'],
                        'url': repo['html_url'],
                        'research_area': area
                    })
        except Exception as e:
            logger.error(f'GitHub API error: {e}')
    
    return results[:limit]

def calculate_relevance_score(paper, research_area: str) -> float:
    """Calculate relevance score for a research paper."""
    score = 0.5  # Base score
    
    # Check title relevance
    if research_area.lower() in paper.title.lower():
        score += 0.2
    
    # Check abstract relevance
    area_keywords = research_area.lower().split()
    abstract_lower = paper.summary.lower()
    keyword_matches = sum(1 for keyword in area_keywords if keyword in abstract_lower)
    score += min(0.3, keyword_matches * 0.1)
    
    return min(1.0, score)

def store_technical_intelligence(results: Dict):
    """Store technical intelligence findings in database."""
    try:
        with sqlite3.connect(SOLOPRENEUR_DB) as conn:
            cursor = conn.cursor()
            
            for source_name, source_data in results['sources'].items():
                for item in source_data:
                    cursor.execute("""
                    INSERT OR IGNORE INTO technical_intelligence 
                    (source, source_id, title, summary, relevance_score, 
                     research_area, url, published_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item['source'],
                        item.get('arxiv_id') or item.get('github_id'),
                        item['title'],
                        item.get('abstract') or item.get('description'),
                        item.get('relevance_score', 0.5),
                        item['research_area'],
                        item['url'],
                        item.get('published_date') or item.get('updated_at')
                    ))
            
            conn.commit()
    except Exception as e:
        logger.error(f'Error storing technical intelligence: {e}')

def generate_schedule_recommendations(patterns: List[sqlite3.Row]) -> List[str]:
    """Generate scheduling recommendations based on energy patterns."""
    recommendations = []
    
    # Find peak hours
    peak_hours = [p['hour'] for p in patterns if p['energy_level'] >= 8]
    if peak_hours:
        recommendations.append(f"Schedule complex tasks during peak hours: {', '.join(map(str, peak_hours))}")
    
    # Find low energy hours
    low_hours = [p['hour'] for p in patterns if p['energy_level'] <= 4]
    if low_hours:
        recommendations.append(f"Reserve low-energy hours for routine tasks: {', '.join(map(str, low_hours))}")
    
    # Find focus windows
    focus_windows = [p['hour'] for p in patterns if p['cognitive_capacity'] >= 8]
    if focus_windows:
        recommendations.append(f"Deep work windows available at: {', '.join(map(str, focus_windows))}")
    
    return recommendations

def optimize_by_energy(tasks: List[Dict], energy_patterns: Dict) -> List[Dict]:
    """Optimize task schedule based on energy levels."""
    # Sort tasks by complexity
    sorted_tasks = sorted(tasks, key=lambda x: x.get('complexity_score', 3), reverse=True)
    
    # Sort hours by energy level
    sorted_hours = sorted(energy_patterns.items(), 
                         key=lambda x: (x[1]['energy'], x[1]['cognitive']), 
                         reverse=True)
    
    optimized = []
    hour_index = 0
    
    for task in sorted_tasks:
        if hour_index < len(sorted_hours):
            hour, energy_data = sorted_hours[hour_index]
            task['scheduled_hour'] = hour
            task['energy_match_score'] = energy_data['energy'] / 10
            optimized.append(task)
            hour_index += 1
    
    return optimized

def optimize_by_deadline(tasks: List[Dict], energy_patterns: Dict) -> List[Dict]:
    """Optimize task schedule based on deadlines."""
    # Sort by deadline/priority
    sorted_tasks = sorted(tasks, key=lambda x: (x.get('priority', 3), -x.get('complexity_score', 3)))
    
    # Assign to available slots
    for i, task in enumerate(sorted_tasks):
        task['scheduled_order'] = i + 1
    
    return sorted_tasks

def optimize_by_complexity(tasks: List[Dict], energy_patterns: Dict) -> List[Dict]:
    """Optimize task schedule based on complexity matching energy."""
    complex_tasks = [t for t in tasks if t.get('complexity_score', 3) >= 4]
    simple_tasks = [t for t in tasks if t.get('complexity_score', 3) < 4]
    
    # Assign complex tasks to high energy hours
    high_energy_hours = [h for h, e in energy_patterns.items() if e['energy'] >= 7]
    low_energy_hours = [h for h, e in energy_patterns.items() if e['energy'] < 7]
    
    optimized = []
    
    for i, task in enumerate(complex_tasks):
        if i < len(high_energy_hours):
            task['scheduled_hour'] = high_energy_hours[i]
            task['optimization_note'] = 'Matched to high energy window'
        optimized.append(task)
    
    for i, task in enumerate(simple_tasks):
        if i < len(low_energy_hours):
            task['scheduled_hour'] = low_energy_hours[i]
            task['optimization_note'] = 'Scheduled for energy conservation'
        optimized.append(task)
    
    return optimized

def generate_schedule_insights(schedule: List[Dict], energy_patterns: Dict) -> Dict:
    """Generate insights about the optimized schedule."""
    insights = {
        'total_tasks': len(schedule),
        'high_complexity_tasks': len([t for t in schedule if t.get('complexity_score', 3) >= 4]),
        'optimization_score': calculate_schedule_optimization_score(schedule, energy_patterns),
        'recommendations': []
    }
    
    # Add specific recommendations
    if insights['optimization_score'] < 0.7:
        insights['recommendations'].append("Consider redistributing tasks for better energy alignment")
    
    return insights

def calculate_schedule_optimization_score(schedule: List[Dict], energy_patterns: Dict) -> float:
    """Calculate how well the schedule aligns with energy patterns."""
    if not schedule or not energy_patterns:
        return 0.0
    
    total_score = 0
    for task in schedule:
        if 'scheduled_hour' in task and task['scheduled_hour'] in energy_patterns:
            energy_level = energy_patterns[task['scheduled_hour']]['energy']
            complexity = task.get('complexity_score', 3)
            
            # Higher score for matching high complexity with high energy
            if complexity >= 4 and energy_level >= 7:
                total_score += 1.0
            elif complexity < 4 and energy_level < 7:
                total_score += 0.8  # Good for energy conservation
            else:
                total_score += 0.4  # Mismatched
    
    return total_score / len(schedule)

def calculate_learning_velocity(progress: sqlite3.Row) -> Dict:
    """Calculate learning velocity and trajectory."""
    if not progress:
        return {'velocity': 0, 'trajectory': 'unknown'}
    
    hours = progress['hours_invested'] or 0
    current_level = progress['current_level'] or 1
    
    if hours > 0:
        velocity = (current_level - 1) / hours  # Levels per hour
        
        # Estimate time to target
        target_level = progress['target_level'] or 5
        remaining_levels = target_level - current_level
        estimated_hours = remaining_levels / velocity if velocity > 0 else float('inf')
        
        return {
            'velocity': velocity,
            'trajectory': 'improving' if velocity > 0 else 'stagnant',
            'estimated_hours_to_target': estimated_hours
        }
    
    return {'velocity': 0, 'trajectory': 'just_started'}

def generate_learning_recommendations(progress: sqlite3.Row) -> List[str]:
    """Generate personalized learning recommendations."""
    recommendations = []
    
    if not progress:
        recommendations.append("Start with foundational concepts and create a learning plan")
        return recommendations
    
    velocity_data = calculate_learning_velocity(progress)
    
    if velocity_data['velocity'] < 0.01:
        recommendations.append("Consider more active learning methods or shorter, focused sessions")
    
    if progress['last_practice_date']:
        last_practice = datetime.fromisoformat(progress['last_practice_date'])
        days_since = (datetime.now() - last_practice).days
        if days_since > 7:
            recommendations.append(f"It's been {days_since} days since last practice. Schedule a review session.")
    
    if progress['current_level'] >= 3 and progress['total_sessions'] < 5:
        recommendations.append("Consider working on a practical project to solidify your knowledge")
    
    return recommendations

def identify_workflow_optimizations(task_patterns: List[Dict], productivity_patterns: List[Dict]) -> List[Dict]:
    """Identify specific workflow optimization opportunities."""
    optimizations = []
    
    # Check estimation accuracy
    for pattern in task_patterns:
        if pattern['estimation_accuracy'] and pattern['estimation_accuracy'] > 1.5:
            optimizations.append({
                'type': 'estimation',
                'task_type': pattern['task_type'],
                'issue': f"Tasks of type '{pattern['task_type']}' take {pattern['estimation_accuracy']:.1f}x longer than estimated",
                'recommendation': "Adjust time estimates or break down tasks into smaller chunks"
            })
    
    # Check productivity patterns
    if productivity_patterns:
        # Find most and least productive hours
        sorted_hours = sorted(productivity_patterns, key=lambda x: x['avg_productivity'] or 0, reverse=True)
        if len(sorted_hours) >= 3:
            best_hours = [h['hour'] for h in sorted_hours[:3]]
            worst_hours = [h['hour'] for h in sorted_hours[-3:]]
            
            optimizations.append({
                'type': 'scheduling',
                'issue': 'Productivity varies significantly by time of day',
                'recommendation': f"Schedule important work during hours {', '.join(best_hours)} and routine tasks during {', '.join(worst_hours)}"
            })
    
    return optimizations

# Export the initialization function
__all__ = ['init_solopreneur_tools']
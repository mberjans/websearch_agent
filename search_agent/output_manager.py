"""Output management for the web search agent system.

This module provides functions for managing output directories, file paths,
and organizing results in a structured manner.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from search_agent.config import Configuration


def create_output_directory_structure(config: Configuration) -> str:
    """
    Create the output directory structure based on configuration.
    
    Args:
        config: Configuration object containing output settings
        
    Returns:
        Path to the created output directory
    """
    if config.output.path:
        # If absolute path is specified, use its directory
        output_dir = os.path.dirname(config.output.path)
    else:
        # Create project-based directory structure
        output_dir = os.path.join(
            config.output.directory,
            config.output.project_name
        )
    
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories for different types of content
    subdirs = ['json', 'html', 'images', 'logs']
    for subdir in subdirs:
        os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
    
    return output_dir


def generate_output_filename(config: Configuration, file_type: str = 'json') -> str:
    """
    Generate a filename for output based on configuration and timestamp.
    
    Args:
        config: Configuration object containing output settings
        file_type: Type of file (json, html, md, etc.)
        
    Returns:
        Generated filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sanitize the query for use in filename
    query_part = "".join(c for c in config.query[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    query_part = query_part.replace(' ', '_')
    
    if query_part:
        filename = f"{config.output.file}_{query_part}_{timestamp}.{file_type}"
    else:
        filename = f"{config.output.file}_{timestamp}.{file_type}"
    
    return filename


def get_full_output_path(config: Configuration, file_type: str = 'json') -> str:
    """
    Get the full output path for a file based on configuration.
    
    Args:
        config: Configuration object containing output settings
        file_type: Type of file (json, html, md, etc.)
        
    Returns:
        Full path where the file should be saved
    """
    if config.output.path:
        # If absolute path is specified, use it directly
        return config.output.path
    
    # Create directory structure
    output_dir = create_output_directory_structure(config)
    
    # Generate filename
    filename = generate_output_filename(config, file_type)
    
    # Determine subdirectory based on file type
    subdir_map = {
        'json': 'json',
        'html': 'html',
        'md': 'json',  # Markdown files go in json directory
        'txt': 'json',  # Text files go in json directory
        'log': 'logs'
    }
    
    subdir = subdir_map.get(file_type, 'json')
    
    return os.path.join(output_dir, subdir, filename)


def save_json_result(result: Dict[str, Any], config: Configuration) -> str:
    """
    Save a result dictionary as JSON to the appropriate output path.
    
    Args:
        result: Result dictionary to save
        config: Configuration object containing output settings
        
    Returns:
        Path where the file was saved
    """
    output_path = get_full_output_path(config, 'json')
    
    # Convert non-serializable objects to strings for JSON serialization
    def convert_for_json(obj):
        if hasattr(obj, '__class__') and obj.__class__.__name__ == 'HttpUrl':
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=convert_for_json, ensure_ascii=False)
    
    return output_path


def save_html_content(html_content: str, url: str, config: Configuration) -> str:
    """
    Save HTML content to the appropriate output path.
    
    Args:
        html_content: HTML content to save
        url: URL where the content was extracted from
        config: Configuration object containing output settings
        
    Returns:
        Path where the file was saved
    """
    # Create a safe filename from the URL
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    path_part = parsed_url.path.replace('/', '_').replace('.', '_')[:30]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{domain}_{path_part}_{timestamp}.html"
    
    output_dir = create_output_directory_structure(config)
    output_path = os.path.join(output_dir, 'html', filename)
    
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def save_image(image_data: bytes, image_url: str, config: Configuration) -> str:
    """
    Save image data to the appropriate output path.
    
    Args:
        image_data: Binary image data
        image_url: URL where the image was extracted from
        config: Configuration object containing output settings
        
    Returns:
        Path where the file was saved
    """
    # Extract file extension from URL
    from urllib.parse import urlparse
    parsed_url = urlparse(image_url)
    path = parsed_url.path
    
    # Get file extension
    if '.' in path:
        extension = path.split('.')[-1].lower()
        if extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
            extension = 'jpg'  # Default extension
    else:
        extension = 'jpg'
    
    # Create a safe filename
    domain = parsed_url.netloc.replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{domain}_{timestamp}.{extension}"
    
    output_dir = create_output_directory_structure(config)
    output_path = os.path.join(output_dir, 'images', filename)
    
    with open(output_path, "wb") as f:
        f.write(image_data)
    
    return output_path


def create_output_summary(config: Configuration, result: Dict[str, Any], output_paths: Dict[str, str]) -> str:
    """
    Create a summary file for the search session.
    
    Args:
        config: Configuration object containing output settings
        result: Result dictionary from the search
        output_paths: Dictionary of file types to their output paths
        
    Returns:
        Path where the summary file was saved
    """
    summary = {
        "session_info": {
            "query": config.query,
            "timestamp": datetime.now().isoformat(),
            "project_name": config.output.project_name,
            "configuration": config.to_dict()
        },
        "results_summary": {
            "synthesized_answer_length": len(result.get("synthesized_answer", {}).get("answer", "")),
            "source_urls_count": len(result.get("source_urls", [])),
            "execution_time_seconds": result.get("execution_time_seconds", 0),
            "evaluation_scores": result.get("evaluation_results", {})
        },
        "output_files": output_paths
    }
    
    output_dir = create_output_directory_structure(config)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = f"session_summary_{timestamp}.json"
    summary_path = os.path.join(output_dir, summary_filename)
    
    with open(summary_path, "w", encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    return summary_path


def get_project_output_directory(project_name: str, base_dir: str = "./output") -> str:
    """
    Get the output directory for a specific project.
    
    Args:
        project_name: Name of the project
        base_dir: Base output directory
        
    Returns:
        Path to the project's output directory
    """
    return os.path.join(base_dir, project_name)


def list_project_sessions(project_name: str, base_dir: str = "./output") -> list:
    """
    List all session files for a specific project.
    
    Args:
        project_name: Name of the project
        base_dir: Base output directory
        
    Returns:
        List of session file paths
    """
    project_dir = get_project_output_directory(project_name, base_dir)
    
    if not os.path.exists(project_dir):
        return []
    
    session_files = []
    json_dir = os.path.join(project_dir, 'json')
    
    if os.path.exists(json_dir):
        for filename in os.listdir(json_dir):
            if filename.endswith('.json') and 'answer_result' in filename:
                session_files.append(os.path.join(json_dir, filename))
    
    return sorted(session_files, reverse=True)  # Most recent first
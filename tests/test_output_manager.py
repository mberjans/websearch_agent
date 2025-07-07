import os
import tempfile
from pathlib import Path
from search_agent.config import Configuration
from search_agent.output_manager import create_output_directory_structure, generate_output_filename, get_full_output_path

def test_create_output_directory_structure():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Configuration.from_env("test query")
        config.output.directory = temp_dir
        config.output.project_name = "test_project"
        output_dir = create_output_directory_structure(config)
        # Check main directory
        assert os.path.exists(output_dir)
        # Check subdirectories
        for subdir in ["json", "html", "images", "logs"]:
            subdir_path = os.path.join(output_dir, subdir)
            assert os.path.exists(subdir_path)
            assert os.path.isdir(subdir_path)

def test_generate_output_filename():
    config = Configuration.from_env("test query for filename generation")
    config.output.file = "resultfile"
    filename = generate_output_filename(config, file_type="json")
    assert filename.startswith("resultfile_test_query_for_filename_generation_")
    assert filename.endswith(".json")

def test_get_full_output_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Configuration.from_env("test query for full path")
        config.output.directory = temp_dir
        config.output.project_name = "test_project"
        config.output.file = "resultfile"
        path = get_full_output_path(config, file_type="json")
        # Should be in the json subdirectory
        assert path.endswith(".json")
        assert os.path.join("test_project", "json") in path
        # Directory should exist
        output_dir = os.path.dirname(os.path.dirname(path))
        assert os.path.exists(output_dir) 
#!/usr/bin/env python3
"""
Orchestration script for automated GitHub activity generation.
Manages state, generates changes, and handles Git/GitHub operations.
"""

import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Git and GitHub imports
try:
    import git
    from github import Github, Auth
    from github.GithubException import RateLimitExceededException
except ImportError:
    git = None
    Github = None
    Auth = None
    RateLimitExceededException = Exception

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).absolute()
        self.state_dir = self.repo_path / "state"
        self.backlog_file = self.state_dir / "backlog.json"
        self.completed_file = self.state_dir / "completed_tasks.json"

        # Load GitHub token from environment
        self.github_token = os.environ.get("GH_TOKEN")
        if not self.github_token:
            logger.warning("GH_TOKEN not set - GitHub operations will be mocked")
            self.github = None
        else:
            self.github = Github(auth=Auth.Token(self.github_token))

        # Initialize git repo
        try:
            self.repo = git.Repo(self.repo_path)
        except Exception as e:
            logger.error(f"Failed to initialize git repo: {e}")
            self.repo = None

    def load_state(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSON state file."""
        if not file_path.exists():
            return []
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            # Try to recover if it's a known corruption pattern (like missing commas or double content)
            # For now, return empty list to avoid crash, but in real scenario we might want more robust recovery
            return []

    def save_state(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        """Save JSON state file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that haven't been completed yet."""
        backlog = self.load_state(self.backlog_file)
        completed = self.load_state(self.completed_file)
        completed_ids = {str(task['id']) for task in completed}
        return [task for task in backlog if str(task['id']) not in completed_ids]

    def select_tasks_for_today(self) -> List[Dict[str, Any]]:
        """Select tasks to work on today (placeholder logic)."""
        pending = self.get_pending_tasks()
        # Return up to 3 pending tasks
        return pending[:3] if pending else []

    def generate_changes(self, task: Dict[str, Any]) -> bool:
        """Generate code changes for a task."""
        logger.info(f"Generating changes for task {task['id']}: {task['description']}")
        
        try:
            # Ensure scripts directory is in path
            import sys
            scripts_dir = str(self.repo_path / "scripts")
            if scripts_dir not in sys.path:
                sys.path.append(scripts_dir)

            from generate_changes import (
                generate_pyspark_change,
                generate_ge_change,
                generate_fastapi_change,
                generate_streamlit_change,
                generate_terraform_change
            )
        except ImportError as e:
            logger.warning(f"Could not import generators: {e}")
            return False

        task_type = task.get("type", "").lower()
        
        try:
            if "pyspark" in task_type or "etl" in task_type:
                generate_pyspark_change()
            elif "ge" in task_type or "expectation" in task_type or "great-expectations" in task_type:
                generate_ge_change()
            elif "fastapi" in task_type or "api" in task_type:
                generate_fastapi_change()
            elif "streamlit" in task_type or "dashboard" in task_type:
                generate_streamlit_change()
            elif "terraform" in task_type or "infra" in task_type:
                generate_terraform_change()
            else:
                # default: add a comment to etl.py
                generate_pyspark_change()
            
            return True
        except Exception as e:
            logger.error(f"Error generating changes: {e}")
            return False

    def create_pull_request(self, branch_name: str, task: Dict[str, Any]) -> bool:
        """Create a pull request."""
        logger.info(f"Creating PR for branch {branch_name}")

        if not self.github:
            logger.warning("GitHub client not available - skipping PR creation")
            return True

        try:
            repo_name = os.environ.get("GITHUB_REPOSITORY")
            if not repo_name:
                logger.warning("GITHUB_REPOSITORY not set - cannot create PR")
                return False

            repo = self.github.get_repo(repo_name)

            # Check if PR already exists
            pulls = repo.get_pulls(state='open', head=f"{repo.owner.login}:{branch_name}")
            if pulls.totalCount > 0:
                logger.info(f"PR already exists for {branch_name}")
                return True

            pr = repo.create_pull(
                title=f"feat: {task['description']}",
                body=f"Task ID: {task['id']}\n\n{task.get('description', '')}\n\nAutomated by GitHub Actions",
                head=branch_name,
                base="main"
            )

            logger.info(f"PR created: {pr.html_url}")
            return True

        except RateLimitExceededException:
            logger.warning("GitHub rate limit exceeded")
            return False
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return False

    def run_daily_cycle(self) -> None:
        """Main orchestration loop."""
        logger.info("Starting daily automation cycle")

        if not self.repo:
            logger.error("No git repo available. Aborting.")
            return

        tasks = self.select_tasks_for_today()
        if not tasks:
            logger.info("No pending tasks found")
            return

        for task in tasks:
            try:
                logger.info(f"Processing task {task['id']}")

                # 1. Ensure we start from main
                self.repo.git.checkout('main')

                # 2. Create feature branch
                branch_name = f"feature/{task['id']}"
                if branch_name in [h.name for h in self.repo.heads]:
                    self.repo.git.branch('-D', branch_name)

                self.repo.git.checkout('-b', branch_name)

                # 3. Generate changes on feature branch
                if not self.generate_changes(task):
                    logger.error(f"Failed to generate changes for {task['id']}")
                    self.repo.git.checkout('main')
                    continue

                # 4. Commit and push feature branch
                if self.repo.is_dirty(untracked_files=True):
                    self.repo.git.add(A=True)
                    self.repo.index.commit(f"feat: {task['description']}")
                    try:
                        self.repo.git.push('origin', branch_name, force=True)
                    except Exception as e:
                        logger.error(f"Failed to push branch {branch_name}: {e}")
                        self.repo.git.checkout('main')
                        continue
                else:
                    logger.info("No changes generated for task")
                    self.repo.git.checkout('main')
                    continue

                # 5. Create PR
                if self.create_pull_request(branch_name, task):
                    # 6. Switch back to main to update state
                    self.repo.git.checkout('main')

                    completed = self.load_state(self.completed_file)
                    completed.append({
                        **task,
                        'completed_at': datetime.now().isoformat(),
                        'branch': branch_name
                    })
                    self.save_state(self.completed_file, completed)

                    # 7. Commit state update on main
                    self.repo.git.add(str(self.completed_file))
                    self.repo.index.commit(f"chore: mark task {task['id']} as completed")
                    logger.info(f"Task {task['id']} marked as completed on main")
                else:
                    logger.error(f"Failed to create PR for {task['id']}")
                    self.repo.git.checkout('main')

            except Exception as e:
                logger.error(f"Error processing task {task['id']}: {e}")
                self.repo.git.checkout('main')

        logger.info("Daily cycle completed. Current branch: %s", self.repo.active_branch.name)

def main():
    orchestrator = Orchestrator()
    orchestrator.run_daily_cycle()

if __name__ == "__main__":
    main()

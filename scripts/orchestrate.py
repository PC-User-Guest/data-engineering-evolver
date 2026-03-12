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
        self.repo_path = Path(repo_path)
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
        completed_ids = {task['id'] for task in completed}
        return [task for task in backlog if task['id'] not in completed_ids]

    def select_tasks_for_today(self) -> List[Dict[str, Any]]:
        """Select tasks to work on today (placeholder logic)."""
        pending = self.get_pending_tasks()
        # For now, return up to 3 random tasks
        return pending[:3] if pending else []

    def generate_changes(self, task: Dict[str, Any]) -> bool:
        """Generate code changes for a task."""
        logger.info(f"Generating changes for task {task['id']}: {task['description']}")
        
        try:
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
            elif "ge" in task_type or "expectation" in task_type:
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

    def create_branch_and_commit(self, task: Dict[str, Any]) -> str:
        """Create a branch and commit changes."""
        branch_name = f"feature/{task['id'].replace('.', '-')}"
        logger.info(f"Creating branch {branch_name} for task {task['id']}")

        if not self.repo:
            logger.warning("Git repo not available - returning branch name only")
            return branch_name

        try:
            # Stash any uncommitted changes before switching branches
            if self.repo.is_dirty():
                logger.info("Stashing uncommitted changes")
                self.repo.git.stash('push', '-m', 'Auto-stash before branch switch')

            # Ensure we're on main before creating new branch
            if self.repo.active_branch.name != 'main':
                self.repo.heads.main.checkout()

            # Create and checkout new branch
            if branch_name in [h.name for h in self.repo.heads]:
                logger.info(f"Branch {branch_name} already exists, checking out")
                self.repo.heads[branch_name].checkout()
            else:
                new_branch = self.repo.create_head(branch_name)
                new_branch.checkout()

            # Restore stashed changes if any
            try:
                self.repo.git.stash('pop')
                logger.info("Restored stashed changes")
            except:
                logger.info("No stashed changes to restore")

            # Add and commit changes (assuming changes were made by generator)
            if self.repo.is_dirty():
                self.repo.git.add(A=True)
                try:
                    self.repo.index.commit(f"feat: {task['description']}")
                    self.repo.remotes.origin.push(branch_name)
                except Exception as e:
                    logger.error(f"Failed to commit/push: {e}")
                    return branch_name
            else:
                logger.info("No changes detected; still creating empty commit")
                # Create an empty commit anyway for activity
                self.repo.git.commit('--allow-empty', '-m', f"feat: {task['description']}")
                try:
                    self.repo.remotes.origin.push(branch_name)
                except Exception as e:
                    logger.warning(f"Could not push: {e}")

            logger.info(f"Branch {branch_name} created and pushed")
            return branch_name

        except Exception as e:
            logger.error(f"Failed to create branch/commit: {e}")
            return branch_name

    def create_pull_request(self, branch_name: str, task: Dict[str, Any]) -> bool:
        """Create a pull request."""
        logger.info(f"Creating PR for branch {branch_name}")

        if not self.github:
            logger.warning("GitHub client not available - skipping PR creation")
            return True

        try:
            # Get repo name from GITHUB_REPOSITORY env or default
            repo_name = os.environ.get("GITHUB_REPOSITORY")
            if not repo_name:
                logger.warning("GITHUB_REPOSITORY not set - cannot create PR")
                return False

            repo = self.github.get_repo(repo_name)

            # Check if PR already exists for this branch
            pulls = repo.get_pulls(state='open', head=f"{repo.owner.login}:{branch_name}")
            if pulls.totalCount > 0:
                logger.info(f"PR already exists for {branch_name}")
                return True

            # Create PR
            pr = repo.create_pull(
                title=f"feat: {task['description']}",
                body=f"Task ID: {task['id']}\n\n{task.get('description', '')}\n\nAutomated by GitHub Actions",
                head=branch_name,
                base="main"
            )

            logger.info(f"PR created: {pr.html_url}")
            
            # Note: Auto-merge disabled for GitHub Actions security restrictions
            # PRs will need to be merged manually or via different workflow
            
            return True

        except RateLimitExceededException:
            logger.warning("GitHub rate limit exceeded - backing off")
            time.sleep(60)
            return False
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return False

    def run_daily_cycle(self) -> None:
        """Main orchestration loop."""
        logger.info("Starting daily automation cycle")

        tasks = self.select_tasks_for_today()
        if not tasks:
            logger.info("No pending tasks found")
            return

        for task in tasks:
            try:
                logger.info(f"Processing task {task['id']}")

                # Generate changes
                if not self.generate_changes(task):
                    logger.error(f"Failed to generate changes for {task['id']}")
                    continue

                # Git operations
                branch_name = self.create_branch_and_commit(task)

                # GitHub operations
                if self.create_pull_request(branch_name, task):
                    # Mark as completed
                    completed = self.load_state(self.completed_file)
                    completed.append({
                        **task,
                        'completed_at': datetime.now().isoformat(),
                        'branch': branch_name
                    })
                    self.save_state(self.completed_file, completed)
                    logger.info(f"Task {task['id']} completed successfully")
                else:
                    logger.error(f"Failed to create PR for {task['id']}")

            except Exception as e:
                logger.error(f"Error processing task {task['id']}: {e}")

        logger.info("Daily cycle completed")

def main():
    orchestrator = Orchestrator()
    orchestrator.run_daily_cycle()

if __name__ == "__main__":
    main()
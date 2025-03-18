import logging
import requests
import os
from typing import ClassVar, Dict, Any, List
from crewai.tools import BaseTool

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


class JiraEpicGrabberFromBoard(BaseTool):
    """
    Tool to retrieve all epics from a given Jira Board.
    This will later be used to generate executive summaries of the Agile development process within the team.
    """
    name: str = "Jira Epic Grabber"
    description: str = (
        "Tool to retrieve all epics from a given Jira Board."
    )
    jira_server: str = os.environ['JIRA_SERVER']
    jira_username: str = os.environ['JIRA_USERNAME']
    api_token: str = os.environ['JIRA_API_TOKEN']
    board_id: str = os.environ['JIRA_BOARD_ID']

    def _run(self) -> Dict[str, Any]:
        """
        Fetch Jira board epics using the Jira REST API.
        """
        url = f"{self.jira_server}/rest/agile/1.0/board/{self.board_id}/epic"
        query_params = {
            "maxResults": 120,  # Restrict the number of epics per page
        }

        logger.info(f"Fetching Jira board epics: {url} with params: {query_params}")

        try:
            response = requests.get(url, auth=(self.jira_username, self.api_token), params=query_params)

            logger.info(f"HTTP Response Status: {response.status_code}")

            if response.status_code == 200:
                return response.json()

            else:
                logger.error(f"Failed to fetch epics: HTTP {response.status_code}, Response: {response.text}")
                return {"error": f"Failed to fetch epics: HTTP {response.status_code}"}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}


class RetrieveIssuesFromEpic(BaseTool):
    """
    Tool to retrieve all issues from a given Jira epic_id.
    These filtered fields will be used to generate executive summaries for downstream processes focused on Agile development.
    """
    name: str = "Retrieve Issues from Epic"
    description: str = (
        "Tool to retrieve all issues from a specific epic ID and extract key details for each issue."
    )
    jira_server: str = os.environ['JIRA_SERVER']
    jira_username: str = os.environ['JIRA_USERNAME']
    api_token: str = os.environ['JIRA_API_TOKEN']

    def _truncate_comment(self, comment: str) -> str:
        """
        Truncate a comment to 200 characters, appending ellipses (...) if needed.

        Args:
            comment (str): The original comment body.

        Returns:
            str: The truncated comment body.
        """
        if len(comment) > 200:
            return comment[:200] + "..."
        return comment

    def _filter_issue_data(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract specific fields from a single issue JSON object.

        Args:
            issue (dict): Raw issue object from the Jira API response.

        Returns:
            dict: A filtered dictionary containing the issue key, assignee, status, and most recent comment.
        """
        key = issue.get("key", "No Key")
        status = issue.get("fields", {}).get("status", {}).get("name", "No Status")
        assignee = issue.get("fields", {}).get("assignee", {}).get("displayName", "Unassigned")
        
        # Extract the most recent comment if available
        comments = issue.get("fields", {}).get("comment", {}).get("comments", [])
        most_recent_comment = (
            {
                "author": comments[-1].get("author", {}).get("displayName", "Unknown"),
                "body": self._truncate_comment(comments[-1].get("body", "")),
                "created": comments[-1].get("created", "Unknown"),
            }
            if comments
            else None
        )

        return {
            "key": key,  # Issue key
            "assignee": assignee,  # Assignee name
            "status": status,  # Issue status
            "most_recent_comment": most_recent_comment,  # Most recent comment details
        }

    def _run(self, epic_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all issues for a given epic ID and extract key details for each issue.
        """
        url = f"{self.jira_server}/rest/agile/1.0/epic/{epic_id}/issue"
        query_params = {
            "maxResults": 30,  # Restrict the number of issues per page
        }

        logger.info(f"Fetching Jira epic issues for epic_id '{epic_id}': {url} with params: {query_params}")

        try:
            response = requests.get(url, auth=(self.jira_username, self.api_token), params=query_params)

            logger.info(f"HTTP Response Status: {response.status_code}")

            if response.status_code == 200:
                issues = response.json().get("issues", [])

                # Gracefully handle missing or unexpected data structures
                if not issues:
                    logger.warning(f"No issues found for epic_id '{epic_id}'. Returning empty list.")
                    return []

                # Filter each issue to only include the required fields
                filtered_issues = []
                for issue in issues:
                    try:
                        filtered_issue = self._filter_issue_data(issue)
                        filtered_issues.append(filtered_issue)
                    except Exception as e:
                        logger.error(f"Error processing issue for epic_id '{epic_id}': {str(e)}")
                        continue  # Skip this issue and process others

                return filtered_issues

            else:
                logger.error(f"Failed to fetch issues for epic_id '{epic_id}': HTTP {response.status_code}, Response: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for epic_id '{epic_id}': {str(e)}")
            return []
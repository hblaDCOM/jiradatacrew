import logging
import yaml  # Add YAML module for reading YAML files
import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from jiradatacrew.tools.custom_tool import JiraEpicGrabberFromBoard, RetrieveIssuesFromEpic

# Configure logging globally
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

@CrewBase
class Jiradatacrew():
    """Jiradatacrew crew"""

    # Load YAML configuration files as dictionaries
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Creating Agents
    @agent
    def data_collection_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_collection_agent']
        )

    # Creating Agents
    @agent
    def report_generation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generation_agent']
        )

    # Creating Tasks
    @task
    def data_collection_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_collection_task'],
            human_input=True,
            tools=[JiraEpicGrabberFromBoard(), RetrieveIssuesFromEpic()],
        )

    @task
    def report_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_generation_task'],
            output_file='output/report.md',
        )
    
    # Creating Crew
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )
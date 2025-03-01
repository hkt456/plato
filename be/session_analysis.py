import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env if present

# Ensure we can import from the AI/LLM folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AI.LLM.groq_llm import GroqLLMClient


class SessionAnalysis:
    def __init__(self, tracker_data: dict, pose_data: dict, session_goal: str):
        """
        Initialize the session analysis with tracker data, pose data, and the user's session goal.
        """
        self.tracker_data = tracker_data
        self.pose_data = pose_data
        self.session_goal = session_goal

        # Process raw data
        self.cleaned_tracker_data = self._clean_tracker_data()
        self.cleaned_pose_data = self._clean_pose_data()
        self.session_duration = self._calculate_session_duration()

    def _clean_tracker_data(self):
        """
        Clean and convert tracker JSON data into a list of dictionaries.
        Each dictionary contains the URL, time spent, and title.
        """
        cleaned_data = []
        for url, details in self.tracker_data.items():
            cleaned_data.append({
                'url': url,
                'time': details.get('time', 0),
                'title': details.get('title', '')
            })
        return cleaned_data

    def _clean_pose_data(self):
        """
        Clean the pose detection data.
        In this case, the input is already a dictionary mapping posture types to durations.
        """
        return self.pose_data

    def _calculate_session_duration(self):
        """
        Calculate the total session duration by summing time spent across all tracked websites.
        """
        return sum(item['time'] for item in self.cleaned_tracker_data)

    def prepare_analysis_context(self):
        """
        Combine session goal, tracker statistics, and posture durations into a context dictionary.
        This context is used to generate the analysis report.
        """
        context = {
            "session_goal": self.session_goal,
            "total_session_duration": self.session_duration,
            "website_usage": self.cleaned_tracker_data,
            "posture_durations": self.cleaned_pose_data
        }
        return context

    def get_analysis_report(self):
        """
        Use the GroqLLMClient to obtain an analysis report based on the session data.
        It builds a prompt from the analysis context and sends it to the Groq-powered LLM.
        """
        # Build a prompt from the analysis context
        context = self.prepare_analysis_context()
        prompt = (
            "Below is the data from a productivity session, where the user aimed to achieve the following goal:\n\n"
            "## Session Goal\n"
            f"{self.session_goal}\n\n"
            "**Note**: All time durations are recorded in seconds.\n\n"
            f"### Session Duration\n"
            f"{self.session_duration}\n\n"
            "### Website Usage\n"
            f"{json.dumps(self.cleaned_tracker_data, indent=2)}\n\n"
            "### Posture Durations\n"
            f"{json.dumps(self.cleaned_pose_data, indent=2)}\n\n"
            "Please provide a comprehensive analysis **in Markdown format** that:\n"
            "1. Evaluates how effectively the user worked toward the session goal.\n"
            "2. Summarizes how time was spent on various websites.\n"
            "3. Discusses the user's posture data and suggests possible improvements.\n"
            "4. Offers actionable recommendations to enhance productivity and maintain better posture.\n\n"
            "Conclude with any additional insights or best practices to help the user structure future sessions more effectively.\n\n"
            "**Important**: Your entire response must be valid Markdown so it can be rendered easily on the front end."
        )

                         
        try:
            # Retrieve API key from environment (which is loaded by dotenv)
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Groq API key not found. Make sure GROQ_API_KEY is set in your environment or .env file.")

            # Create the GroqLLMClient with the retrieved API key
            groq_client = GroqLLMClient(api_key=api_key)

            # Send the prompt to the LLM
            analysis_report = groq_client.chat_completion(prompt)
            return analysis_report

        except Exception as e:
            print(f"Error obtaining analysis report from Groq LLM: {e}")
            return None


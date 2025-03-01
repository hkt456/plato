'use client';
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import ReactMarkdown from "react-markdown";

const data = [
  { name: "Google", value: 20 },
  { name: "NTULearn", value: 14 },
  { name: "Linkedin", value: 7 },
  { name: "Youtube", value: 7 },
  { name: "Wikipedia", value: 3 },
  { name: "ChatGPT", value: 3 },
  { name: "Gemini", value: 3 },
  { name: "Outlook", value: 1 }
];

const analysisReport = `### Session Analysis
#### Effectiveness in Achieving the Session Goal
The user's goal for the session was to complete coding tasks efficiently. Given the short session duration of approximately 13 seconds, it's challenging to assess the effectiveness of achieving this goal. However, the fact that the user spent time on http://127.0.0.1:8000/usage and http://127.0.0.1:8000/usage_json suggests that some effort was made towards coding or related tasks. The time spent on these tasks is too brief to draw conclusive insights, but it indicates an attempt to work towards the goal.

#### Summary of Time Spent on Websites
The user spent time on three different websites:
- https://chatgpt.com/c/67c2317b-594c-800b-b5d8-014c3e4fbc0b: Approximately 3 seconds
- http://127.0.0.1:8000/usage: Approximately 8 seconds
- http://127.0.0.1:8000/usage_json: Approximately 2 seconds

The majority of the time (about 8 seconds) was spent on http://127.0.0.1:8000/usage, which could be related to monitoring or managing usage, possibly related to coding tasks or development environment.

#### Posture Data Analysis and Suggestions
The posture durations indicate that the user spent time in less-than-ideal postures:
- *Humpedback*: 3 seconds
- *Wrong distance*: 4 seconds
- *Shoulder deviation*: 5 seconds

These posture issues can lead to discomfort and health problems over time. To improve posture:
- *Regular Breaks*: Take breaks every 25-30 minutes to stand up, stretch, and move around.
- *Ergonomic Setup*: Ensure the workspace is set up to promote good posture, including the position of the monitor, chair height, and keyboard placement.
- *Posture Reminders*: Use apps or alarms to remind oneself to check and correct posture throughout the day.

#### Actionable Recommendations
To enhance productivity and maintain better posture:
- *Session Length*: Increase the session duration to allow for more substantial progress on coding tasks.
- *Focus*: Minimize time spent on non-essential websites, and allocate more time for coding and development.
- *Posture Correction*: Implement the suggested posture improvements and regularly check posture during work sessions.
- *Break Reminders*: Use tools or apps that remind you to take breaks and stretch to avoid prolonged periods in poor postures.

### Additional Insights and Best Practices
For future sessions, consider the following:
- *Set Specific Objectives*: Define clear, achievable objectives for each session to maintain focus.
- *Use Time Management Tools*: Utilize tools like the Pomodoro Timer to enhance productivity and break times.
- *Regular Review*: Regularly review session data to identify patterns, strengths, and areas for improvement.
- *Health and Wellness*: Prioritize health and wellness by incorporating exercise, healthy eating, and adequate sleep to support productivity and posture.

By following these recommendations and insights, the user can structure future sessions more effectively, leading to improved productivity, better posture, and overall well-being.`;

const PostureUI = () => {
  const router = useRouter();
  const [postureData, setPostureData] = useState<Record<string, number> | null>(null);

  useEffect(() => {
    // Fetch posture data from the backend
    const fetchPostureData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/get_summary");
        const data = await response.json();
        setPostureData(data);
      } catch (error) {
        console.error("Error fetching posture data:", error);
      }
    };

    fetchPostureData();
  }, []);

  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch data for analysis from the backend
    const fetchReport = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/analysis_report", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ session_goal: "Complete coding tasks efficiently" }),
        });

        const data = await response.json();
        if (data.error) {
          setError(data.error);
        } else {
          setReport(data.analysis_report);
        }
      } catch (err) {
        setError("Failed to fetch report.");
      }
    };

    fetchReport();
  }, []);

  return (
    <div className="flex flex-col items-center bg-[#fdf8fc] p-6 min-h-screen text-center">
      {/* Timer */}
      <div className="text-2xl font-bold bg-gradient-to-r from-pink-500 to-purple-500 text-white py-2 px-6 rounded-full mb-4">
        03:45
      </div>
      
      {/* Bar Chart */}
      <div className="w-full max-w-3xl h-64 bg-white p-4 rounded-lg shadow">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="url(#gradient)" />
            <defs>
              <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ff007a" />
                <stop offset="100%" stopColor="#6a0dad" />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Posture Stats */}
      <div className="grid grid-cols-2 gap-4 w-full max-w-3xl my-4">
        {postureData ? (
          Object.entries(postureData).map(([posture, duration]) => (
            <div key={posture} className="text-lg font-bold">
              {posture} <br />
              <span className="text-gray-500">{duration.toFixed(2)} seconds</span>
            </div>
          ))
        ) : (
          <p>Loading posture data...</p>
        )}
      </div>
      
      {/* Summary */}
      <div className="max-w-3xl text-left bg-white p-4 rounded-lg shadow">
        <h2 className="font-bold">SUMMARY</h2>
        {error ? (
          <p className="text-red-500">{error}</p>
        ) : report ? (
          <ReactMarkdown className="prose">{report}</ReactMarkdown>
        ) : (
          <p>Loading...</p>
        )}
      </div>
      
      {/* Continue Button */}
      <button onClick={() => router.push("/session")}
        className="mt-8 px-8 py-4 text-xl bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-full shadow-md hover:opacity-90">
        Continue
      </button>
    </div>
  );
};

export default PostureUI;

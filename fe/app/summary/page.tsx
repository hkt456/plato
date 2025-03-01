'use client';
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import ReactMarkdown from "react-markdown";

const PostureUI = () => {
  const router = useRouter();
  const [postureData, setPostureData] = useState<Record<string, number> | null>(null);
  const [usageData, setUsageData] = useState<{ name: string; value: number }[]>([]);
  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPostureData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/get_summary");
        const data = await response.json();
        setPostureData(data);
      } catch (error) {
        console.error("Error fetching posture data:", error);
      }
    };
    
    const fetchUsageData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/usage");
        const data = await response.json();
        const formattedData = Object.keys(data).map((key) => ({
          name: data[key].title as string,
          value: data[key].time as number,
        }));
        setUsageData(formattedData);
      } catch (error) {
        console.error("Error fetching usage data:", error);
      }
    };
    
    fetchPostureData();
    fetchUsageData();
  }, []);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/analysis_report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
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
          <BarChart data={usageData}>
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
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

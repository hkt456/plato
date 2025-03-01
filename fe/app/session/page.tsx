'use client';

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const SessionTimer = () => {
  const router = useRouter();
  const [time, setTime] = useState(60); // 60 seconds for testing
  const [imgSrc, setImgSrc] = useState<string | null>(null);

  useEffect(() => {
    // Open the WebSocket connection
    const ws = new WebSocket("ws://localhost:8000/video");

    ws.onopen = () => {
      console.log("WebSocket connected to /video");
    };

    ws.onmessage = (event) => {
      const base64Data = event.data as string;
      setImgSrc(`data:image/jpeg;base64,${base64Data}`);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    // Clean up on unmount
    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    // When the timer starts, mark the session as running
    sessionStorage.setItem("running", "true");

    if (time === 0) {
      handleTimeEnd();
      return;
    }

    const timer = setInterval(() => {
      setTime((prevTime) => (prevTime > 0 ? prevTime - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, [time]);

  const handleTimeEnd = () => {
    // Set session as not running before navigating
    sessionStorage.setItem("running", "false");
    router.push("/analysis");
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-pink-50 text-gray-900 relative">
      {/* Timer Display */}
      <div className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full text-5xl font-bold absolute top-10">
        {formatTime(time)}
      </div>

      {/* Live Video Feed */}
      {imgSrc ? (
        <img
          src={imgSrc}
          alt="Live Video"
          className="mt-24 border-4 border-purple-500 rounded-lg"
          width={640}
          height={384}
        />
      ) : (
        <p className="mt-24 text-xl">Connecting to camera feed...</p>
      )}

      {/* End Session Button */}
      <button
        onClick={() => {
          sessionStorage.setItem("running", "false");
          router.push("/");
        }}
        className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full text-2xl font-bold absolute bottom-20"
      >
        END SESSION
      </button>
    </div>
  );
};

export default SessionTimer;


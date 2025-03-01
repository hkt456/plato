"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const SessionTimer = () => {
  const router = useRouter();
  const [time, setTime] = useState(3); // 25 minutes in seconds

  useEffect(() => {
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

      {/* END SESSION Button with increased padding, font size, and spacing */}
      <button
        onClick={() => router.push("/")}
        className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full text-2xl font-bold absolute bottom-20"
      >
        END SESSION
      </button>
    </div>
  );
};

export default SessionTimer;
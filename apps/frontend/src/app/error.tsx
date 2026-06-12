'use client';

import { useEffect } from 'react';

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-neutral-950 text-white font-sans p-4">
      <div className="max-w-md p-8 border border-red-500/30 bg-red-950/20 rounded-xl text-center space-y-6 shadow-2xl shadow-red-500/10">
        <h2 className="text-2xl font-semibold tracking-tight text-red-500">
          Terminal Failure Detected
        </h2>
        <p className="text-neutral-400 text-sm">
          A critical error occurred in the ASTRA-X platform. Please try recovering the session.
        </p>
        <button
          onClick={() => reset()}
          className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-950"
        >
          Recover Session
        </button>
      </div>
    </div>
  );
}

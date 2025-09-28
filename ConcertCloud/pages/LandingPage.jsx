import React, { useState, useEffect } from "react";
import { Search, Plus } from "lucide-react";

// Landing screen for ConcertCloud
// - Tailwind CSS for styling
// - Lucide icons for search/plus
// - Subtle animated musical notes + cloud shapes
// - Accessible labels & keyboard handling

export default function LandingPage() {
  const [query, setQuery] = useState("");

  function handleSearch() {
    if (!query.trim()) return;
    // TODO: wire to /search?q=...
    console.log("Search:", query);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleSearch();
  }

  function onSignUp() {
    // TODO: navigate to signup route
    console.log("Sign up clicked");
  }

  function onLogin() {
    // TODO: navigate to login route
    console.log("Login clicked");
  }

  // (Optional) small floating animation for musical notes
  useEffect(() => {
    const style = document.createElement("style");
    style.innerHTML = `
      @keyframes floatY { 0%{ transform: translateY(0) rotate(0deg);} 50%{transform: translateY(-10px) rotate(6deg);} 100%{ transform: translateY(0) rotate(0deg);} }
      @keyframes drift { 0%{ transform: translateX(0);} 100%{ transform: translateX(30px);} }
    `;
    document.head.appendChild(style);
    return () => { document.head.removeChild(style); };
  }, []);

  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-b from-purple-900 via-fuchsia-700 to-purple-600 text-white">
      {/* Decorative musical notes */}
      <Notes />

      {/* Content wrapper */}
      <div className="relative mx-auto flex min-h-screen w-full max-w-5xl flex-col items-center justify-center px-6 text-center">
        <h1 className="select-none drop-shadow-xl text-5xl sm:text-6xl md:text-8xl font-extrabold tracking-tight">
          <span className="text-white">Concert</span>
          <span className="ml-2 bg-gradient-to-r from-pink-300 via-fuchsia-300 to-purple-200 bg-clip-text text-transparent">Cloud</span>
        </h1>

        <p className="mt-5 text-base sm:text-lg md:text-xl text-fuchsia-100/90 max-w-2xl">
          Everyone Deserves to see their Favourite Artist
        </p>

        {/* Search Bar */}
        <div className="mt-10 w-full max-w-2xl">
          <div className="flex items-center gap-2 rounded-2xl bg-fuchsia-200/40 p-2 pl-4 shadow-xl ring-1 ring-white/10 backdrop-blur">
            <Search aria-hidden className="h-5 w-5 text-fuchsia-100" />
            <input
              aria-label="Search for artists, venues, events"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search artists, venues, or events"
              className="w-full bg-transparent placeholder-fuchsia-100/70 text-white outline-none px-2 py-3 text-sm sm:text-base"
            />
            <button
              onClick={handleSearch}
              className="group inline-flex items-center justify-center rounded-xl bg-pink-400/90 px-3 py-2 font-semibold text-purple-900 shadow hover:bg-pink-300 focus:outline-none focus:ring-2 focus:ring-white/50"
              aria-label="Add filter or search"
            >
              <Plus className="h-5 w-5 transition-transform group-active:scale-95" />
            </button>
          </div>
        </div>

        {/* CTAs */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <button onClick={onSignUp} className="rounded-2xl bg-white/90 px-8 py-3 font-semibold text-purple-800 shadow-lg hover:bg-white/95 focus:outline-none focus:ring-2 focus:ring-white/60">
            Sign Up
          </button>
          <button onClick={onLogin} className="rounded-2xl bg-fuchsia-300/90 px-8 py-3 font-semibold text-purple-900 shadow-lg hover:bg-fuchsia-300 focus:outline-none focus:ring-2 focus:ring-white/60">
            Login
          </button>
        </div>
      </div>

      {/* Cloud shapes at bottom */}
      <Clouds />
    </main>
  );
}

function Notes() {
  // Cluster of musical note emojis positioned around edges
  const notes = [
    { left: "4%", top: "18%", size: "text-3xl", rot: "-rotate-6" },
    { left: "10%", top: "44%", size: "text-2xl", rot: "rotate-3" },
    { left: "16%", top: "70%", size: "text-3xl", rot: "-rotate-2" },
    { right: "6%", top: "22%", size: "text-3xl", rot: "rotate-6" },
    { right: "12%", top: "46%", size: "text-2xl", rot: "-rotate-3" },
    { right: "8%", top: "72%", size: "text-3xl", rot: "rotate-2" },
  ];
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 select-none">
      {notes.map((n, i) => (
        <div
          key={i}
          className={`absolute ${n.size} ${n.rot} text-fuchsia-200/30 animate-[floatY_6s_ease-in-out_infinite]`}
          style={{ left: n.left, right: n.right, top: n.top }}
        >
          🎵
        </div>
      ))}
    </div>
  );
}

function Clouds() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-x-0 bottom-0 h-64">
      <div className="absolute -bottom-10 left-[-10%] h-72 w-72 rounded-full bg-fuchsia-300/40 blur-2xl" />
      <div className="absolute -bottom-16 left-[10%] h-80 w-80 rounded-full bg-fuchsia-200/40 blur-2xl" />
      <div className="absolute -bottom-20 left-[35%] h-72 w-96 rounded-full bg-pink-300/40 blur-2xl" />
      <div className="absolute -bottom-14 right-[15%] h-72 w-80 rounded-full bg-fuchsia-200/40 blur-2xl" />
      <div className="absolute -bottom-8 right-[-8%] h-64 w-64 rounded-full bg-fuchsia-300/40 blur-2xl" />
    </div>
  );
}

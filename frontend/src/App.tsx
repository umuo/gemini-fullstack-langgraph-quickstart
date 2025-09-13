import { Routes, Route } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { ResearchAssistant } from "@/components/ResearchAssistant";
import { ExamGenerator } from "@/components/ExamGenerator";

export default function App() {
  return (
    <div className="flex flex-col h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <Navigation />
      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<ExamGenerator />} />
          <Route path="/research" element={<ResearchAssistant />} />
          <Route path="/exam" element={<ExamGenerator />} />
        </Routes>
      </main>
    </div>
  );
}

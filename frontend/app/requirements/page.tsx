"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { 
  Brain, FileText, ListTodo, Layers, ArrowRight, 
  Sparkles, Zap, Shield, Cpu, Terminal, CheckCircle2
} from "lucide-react";
import { Sidebar } from "@/components/layout/sidebar";

export default function RequirementsPage() {
  const [input, setInput] = useState("");
  const [isParsing, setIsParsing] = useState(false);
  const [spec, setSpec] = useState<any>(null);

  const handleParse = async () => {
    if (!input.trim()) return;
    setIsParsing(true);
    // Simulation of API call to /api/v1/engineering/parse-requirements
    await new Promise(r => setTimeout(r, 2500));
    setSpec({
      project_name: "Nexus Analytics Pro",
      summary: "An enterprise-grade real-time analytics platform.",
      features: [
        { id: "F001", name: "Real-time Dashboard", priority: "critical" },
        { id: "F002", name: "AI Insight Engine", priority: "high" },
        { id: "F003", name: "Multi-tenant Auth", priority: "medium" }
      ],
      architecture: "Event-Driven Microservices",
      stack: {
        backend: ["FastAPI", "Kafka", "PostgreSQL"],
        frontend: ["Next.js 15", "Tailwind CSS", "Recharts"]
      }
    });
    setIsParsing(false);
  };

  return (
    <div className="flex min-h-screen bg-nexus-void text-nexus-text">
      <Sidebar />
      <main className="ml-[72px] flex-1 p-8 grid-bg">
        <div className="max-w-5xl mx-auto">
          <header className="mb-10">
            <h1 className="text-4xl font-black mb-4 flex items-center gap-3">
              <Brain className="text-nexus-primary" size={32} />
              <span className="gradient-text">Autonomous Requirements Engine</span>
            </h1>
            <p className="text-nexus-muted max-w-2xl">
              Input your product vision, GitHub issues, or architecture diagrams. NEXUS OS will semantically decompose them into engineering specs.
            </p>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <div className="space-y-6">
              <div className="nexus-card p-6 flex flex-col h-[400px]">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xs font-bold uppercase tracking-widest text-nexus-muted">Raw Vision Input</h2>
                  <div className="flex gap-2">
                    <span className="px-2 py-0.5 rounded bg-nexus-elevated text-[9px] text-nexus-primary border border-nexus-primary/20">TEXT</span>
                    <span className="px-2 py-0.5 rounded bg-nexus-elevated text-[9px] text-nexus-muted border border-nexus-border">GITHUB</span>
                  </div>
                </div>
                <textarea 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe your project requirements in detail..."
                  className="flex-1 bg-black/50 border border-nexus-border rounded-xl p-4 text-sm focus:border-nexus-primary outline-none resize-none transition-colors"
                />
                <button 
                  onClick={handleParse}
                  disabled={isParsing || !input.trim()}
                  className="btn-primary mt-4 py-3 flex items-center justify-center gap-2 group disabled:opacity-50"
                >
                  {isParsing ? (
                    <motion.div 
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                    />
                  ) : (
                    <Sparkles size={16} />
                  )}
                  {isParsing ? "Reasoning..." : "Generate Engineering Spec"}
                  <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </button>
              </div>

              {/* Tips / Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="nexus-card p-4 border-l-2 border-l-nexus-primary">
                  <Shield size={16} className="text-nexus-primary mb-2" />
                  <h3 className="text-xs font-bold mb-1">Semantic Parsing</h3>
                  <p className="text-[10px] text-nexus-muted">Uses GPT-4o for deep contextual understanding of requirements.</p>
                </div>
                <div className="nexus-card p-4 border-l-2 border-l-nexus-emerald">
                  <Layers size={16} className="text-nexus-emerald mb-2" />
                  <h3 className="text-xs font-bold mb-1">Architecture Inference</h3>
                  <p className="text-[10px] text-nexus-muted">Automatically selects the best design patterns for your scale.</p>
                </div>
              </div>
            </div>

            {/* Result Section */}
            <div className="space-y-6">
              <AnimatePresence mode="wait">
                {spec ? (
                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="nexus-card p-6 min-h-[400px] border-nexus-primary/30"
                  >
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-sm font-bold text-nexus-primary flex items-center gap-2">
                        <CheckCircle2 size={16} />
                        Structured Specification
                      </h2>
                      <button className="text-[10px] text-nexus-muted hover:text-white transition-colors">EXPORT PRD</button>
                    </div>

                    <div className="space-y-6">
                      <div>
                        <h3 className="text-xs font-bold text-white mb-2 uppercase tracking-wide">Project Scope</h3>
                        <p className="text-sm font-bold gradient-text">{spec.project_name}</p>
                        <p className="text-[11px] text-nexus-muted mt-1">{spec.summary}</p>
                      </div>

                      <div>
                        <h3 className="text-xs font-bold text-white mb-3 uppercase tracking-wide">Feature Breakdown</h3>
                        <div className="space-y-2">
                          {spec.features.map((f: any) => (
                            <div key={f.id} className="flex items-center justify-between p-2 rounded bg-white/5 border border-nexus-border">
                              <span className="text-[11px] font-mono text-nexus-primary">{f.id}</span>
                              <span className="text-[11px] flex-1 px-3">{f.name}</span>
                              <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${f.priority === 'critical' ? 'text-nexus-rose bg-nexus-rose/10' : 'text-nexus-amber bg-nexus-amber/10'}`}>
                                {f.priority}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h3 className="text-xs font-bold text-white mb-2 uppercase tracking-wide">Inferred Stack</h3>
                          <div className="flex flex-wrap gap-1">
                            {spec.stack.backend.map((s: any) => (
                              <span key={s} className="text-[9px] px-1.5 py-0.5 rounded bg-nexus-elevated border border-nexus-border">{s}</span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h3 className="text-xs font-bold text-white mb-2 uppercase tracking-wide">Architecture</h3>
                          <div className="text-[11px] font-bold text-nexus-cyan flex items-center gap-1">
                            <Layers size={10} />
                            {spec.architecture}
                          </div>
                        </div>
                      </div>

                      <button className="btn-primary w-full py-3 rounded-xl flex items-center justify-center gap-2 mt-4 shadow-lg shadow-indigo-500/20">
                        <Cpu size={16} />
                        Commit to Engineering Workforce
                      </button>
                    </div>
                  </motion.div>
                ) : (
                  <div className="nexus-card p-6 min-h-[400px] flex flex-col items-center justify-center text-center opacity-50 grayscale">
                    <Brain size={48} className="text-nexus-border mb-4 animate-float" />
                    <h2 className="text-sm font-bold text-nexus-muted">Awaiting Requirements Input</h2>
                    <p className="text-[11px] text-nexus-muted max-w-[200px] mt-2 italic">Structured data will be displayed here after reasoning.</p>
                  </div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

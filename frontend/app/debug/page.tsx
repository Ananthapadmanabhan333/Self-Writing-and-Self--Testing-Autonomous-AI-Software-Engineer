"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { 
  Bug, Search, AlertCircle, RefreshCw, 
  ChevronRight, Terminal, CheckCircle2, History,
  ShieldCheck, Zap, Code2, Play
} from "lucide-react";
import { Sidebar } from "@/components/layout/sidebar";
import Editor from "@monaco-editor/react";

const RECENT_FAILURES = [
  { id: "ERR-921", title: "Connection Timeout in Database Pool", severity: "high", status: "investigating", timestamp: "12m ago" },
  { id: "ERR-918", title: "Syntax Error in generated_auth_middleware.py", severity: "critical", status: "patch_ready", timestamp: "45m ago" },
  { id: "ERR-915", title: "Flaky Test: test_concurrent_writes", severity: "medium", status: "replaying", timestamp: "2h ago" },
  { id: "ERR-902", title: "Memory Leak detected in Worker Node", severity: "high", status: "fixed", timestamp: "Yesterday" },
];

export default function DebugCockpit() {
  const [selectedError, setSelectedError] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async (error: any) => {
    setSelectedError(error);
    setIsAnalyzing(true);
    await new Promise(r => setTimeout(r, 2000));
    setIsAnalyzing(false);
  };

  return (
    <div className="flex min-h-screen bg-nexus-void text-nexus-text">
      <Sidebar />
      <main className="ml-[72px] flex-1 p-8 grid-bg overflow-hidden flex flex-col h-screen">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black mb-2 flex items-center gap-3">
              <Bug className="text-nexus-amber" size={32} />
              <span className="gradient-text-warm">Autonomous Debugging Cockpit</span>
            </h1>
            <p className="text-nexus-muted">Self-healing failure analysis and recursive patch generation.</p>
          </div>
          <div className="flex gap-4">
            <div className="nexus-card px-4 py-2 flex flex-col items-center justify-center">
              <span className="text-[10px] uppercase font-bold text-nexus-muted">Auto-Fixed</span>
              <span className="text-lg font-bold text-nexus-emerald">934</span>
            </div>
            <div className="nexus-card px-4 py-2 flex flex-col items-center justify-center">
              <span className="text-[10px] uppercase font-bold text-nexus-muted">Resolution Rate</span>
              <span className="text-lg font-bold text-nexus-primary">98.2%</span>
            </div>
          </div>
        </header>

        <div className="flex-1 flex gap-6 overflow-hidden">
          {/* Failure Feed */}
          <div className="w-1/3 flex flex-col gap-4 overflow-y-auto pr-2 custom-scrollbar">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-bold uppercase tracking-widest text-nexus-muted">Incident Feed</h2>
              <RefreshCw size={14} className="text-nexus-muted hover:text-white cursor-pointer transition-colors" />
            </div>
            {RECENT_FAILURES.map((err, i) => (
              <motion.div 
                key={err.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => handleAnalyze(err)}
                className={`nexus-card p-4 cursor-pointer transition-all border-l-4 ${
                  selectedError?.id === err.id ? 'bg-nexus-primary/10 border-nexus-primary' : 
                  err.severity === 'critical' ? 'border-nexus-rose' : 
                  err.severity === 'high' ? 'border-nexus-amber' : 'border-nexus-cyan'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-nexus-muted">{err.id}</span>
                  <span className="text-[9px] text-nexus-text-dim">{err.timestamp}</span>
                </div>
                <h3 className="text-xs font-bold mb-3 line-clamp-1">{err.title}</h3>
                <div className="flex items-center justify-between">
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                    err.status === 'fixed' ? 'text-nexus-emerald bg-nexus-emerald/10' :
                    err.status === 'investigating' ? 'text-nexus-primary bg-nexus-primary/10' :
                    'text-nexus-amber bg-nexus-amber/10'
                  }`}>
                    {err.status.replace('_', ' ')}
                  </span>
                  <ChevronRight size={14} className="text-nexus-border" />
                </div>
              </motion.div>
            ))}
          </div>

          {/* Analysis View */}
          <div className="flex-1 flex flex-col gap-6 overflow-hidden">
            <AnimatePresence mode="wait">
              {selectedError ? (
                <motion.div 
                  key={selectedError.id}
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  className="flex-1 flex flex-col gap-6"
                >
                  {/* Root Cause Card */}
                  <div className="nexus-card p-6 border-nexus-primary/20 relative overflow-hidden">
                    {isAnalyzing && (
                      <motion.div 
                        initial={{ x: "-100%" }}
                        animate={{ x: "100%" }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                        className="absolute top-0 left-0 w-full h-[1px] bg-nexus-primary"
                      />
                    )}
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-sm font-bold flex items-center gap-2">
                        <Zap size={16} className="text-nexus-primary" />
                        Root Cause Analysis
                      </h2>
                      <div className="flex items-center gap-2 text-[10px] font-bold text-nexus-emerald">
                        <ShieldCheck size={14} />
                        Confidence: 94%
                      </div>
                    </div>

                    {isAnalyzing ? (
                      <div className="flex flex-col items-center justify-center h-24 text-nexus-muted italic animate-pulse">
                        Agent is performing deep stack trace traversal...
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <p className="text-sm text-gray-300 bg-black/50 p-3 border border-nexus-border rounded-lg">
                          "The syntax error in <span className="text-nexus-primary">generated_auth_middleware.py</span> was caused by an unclosed parentheses on line 42, which originated from a malformed JSON output during the Agent reasoning phase."
                        </p>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-3 rounded-lg bg-white/5 border border-nexus-border">
                            <h3 className="text-[10px] font-bold text-nexus-muted uppercase mb-1">Impact</h3>
                            <p className="text-xs text-nexus-rose font-bold">Prevents build success</p>
                          </div>
                          <div className="p-3 rounded-lg bg-white/5 border border-nexus-border">
                            <h3 className="text-[10px] font-bold text-nexus-muted uppercase mb-1">Category</h3>
                            <p className="text-xs text-nexus-primary font-bold">Agent Logic Error</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Patch Preview */}
                  <div className="flex-1 nexus-card overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-nexus-border flex items-center justify-between bg-nexus-deep">
                      <div className="flex items-center gap-3">
                        <Code2 size={16} className="text-nexus-primary" />
                        <h2 className="text-xs font-bold uppercase tracking-widest text-nexus-muted">Autonomous Patch Proposal</h2>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-3 py-1 bg-nexus-elevated border border-nexus-border rounded text-[10px] hover:border-nexus-primary transition-all">REJECT</button>
                        <button className="btn-primary px-3 py-1 rounded text-[10px]">APPLY FIX</button>
                      </div>
                    </div>
                    <div className="flex-1 relative">
                      <Editor
                        height="100%"
                        theme="vs-dark"
                        defaultLanguage="python"
                        value={`# --- PATCH PROPOSAL: generated_auth_middleware.py ---
# FIXED: Unclosed parentheses in auth check

async def check_auth(token: str):
-   if not validate_token(token:
+   if not validate_token(token):
        raise HTTPException(status_code=401)
`}
                        options={{
                          fontSize: 12,
                          readOnly: true,
                          minimap: { enabled: false }
                        }}
                      />
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center opacity-30">
                  <Terminal size={64} className="text-nexus-border mb-4" />
                  <h2 className="text-lg font-bold">Select an incident to begin analysis</h2>
                  <p className="text-sm max-w-[300px] mt-2">The Debug Agent will provide root cause analysis and patch suggestions here.</p>
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  );
}

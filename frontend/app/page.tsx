"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import {
  Zap, ArrowRight, Play, Brain, Cpu, Bug, Rocket,
  GitBranch, Activity, CheckCircle2, Clock, AlertTriangle,
} from "lucide-react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/sidebar";

const STATS = [
  { label: "Tasks Completed", value: "2,847", delta: "+12 today", color: "#10b981", icon: CheckCircle2 },
  { label: "Code Files Generated", value: "18,923", delta: "+247 today", color: "#6366f1", icon: Cpu },
  { label: "Bugs Auto-Fixed", value: "934", delta: "+8 today", color: "#fb923c", icon: Bug },
  { label: "Deployments", value: "312", delta: "+3 today", color: "#f59e0b", icon: Rocket },
];

const AGENT_STATUS = [
  { name: "Architect Agent",  status: "standby", type: "architect" },
  { name: "Backend Agent",    status: "standby", type: "backend"   },
  { name: "Frontend Agent",   status: "standby", type: "frontend"  },
  { name: "DevOps Agent",     status: "standby", type: "devops"    },
  { name: "QA Agent",         status: "standby", type: "qa"        },
  { name: "Security Agent",   status: "standby", type: "security"  },
  { name: "Debug Agent",      status: "standby", type: "debug"     },
  { name: "Refactor Agent",   status: "standby", type: "refactor"  },
  { name: "SRE Agent",        status: "standby", type: "sre"       },
  { name: "Release Agent",    status: "standby", type: "release"   },
];

const AGENT_COLORS: Record<string, string> = {
  architect: "#6366f1", backend: "#06b6d4", frontend: "#8b5cf6",
  devops: "#f59e0b", qa: "#10b981", security: "#f43f5e",
  debug: "#fb923c", refactor: "#a78bfa", sre: "#34d399", release: "#60a5fa",
};

function AgentCard({ agent }: { agent: typeof AGENT_STATUS[0] }) {
  const color = AGENT_COLORS[agent.type];
  return (
    <motion.div
      className="nexus-card p-3 flex items-center gap-3"
      whileHover={{ scale: 1.01 }}
    >
      <div
        className="w-2 h-2 rounded-full flex-shrink-0"
        style={{
          background: agent.status === "running" ? color : "#374151",
          boxShadow: agent.status === "running" ? `0 0 8px ${color}` : "none",
        }}
      />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-gray-300 truncate">{agent.name}</p>
        <p className="text-[10px] text-gray-600 uppercase tracking-wide">{agent.status}</p>
      </div>
      <div
        className="text-[10px] px-2 py-0.5 rounded-full"
        style={{ background: `${color}15`, color }}
      >
        ready
      </div>
    </motion.div>
  );
}

export default function Dashboard() {
  const [requirement, setRequirement] = useState("");
  const [isLaunching, setIsLaunching] = useState(false);
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number }>>([]);

  useEffect(() => {
    setParticles(
      Array.from({ length: 20 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
      }))
    );
  }, []);

  const handleLaunch = async () => {
    if (!requirement.trim()) return;
    setIsLaunching(true);
    await new Promise((r) => setTimeout(r, 1500));
    setIsLaunching(false);
    window.location.href = `/engineering?req=${encodeURIComponent(requirement)}`;
  };

  return (
    <div className="flex min-h-screen bg-nexus-void">
      <Sidebar />

      <main className="ml-[72px] flex-1 min-h-screen grid-bg overflow-hidden">
        {/* Ambient particles */}
        <div className="fixed inset-0 pointer-events-none">
          {particles.map((p) => (
            <motion.div
              key={p.id}
              className="absolute w-1 h-1 rounded-full bg-indigo-500/20"
              style={{ left: `${p.x}%`, top: `${p.y}%` }}
              animate={{ opacity: [0.1, 0.6, 0.1], scale: [1, 1.5, 1] }}
              transition={{ duration: 3 + Math.random() * 4, repeat: Infinity, delay: Math.random() * 3 }}
            />
          ))}
        </div>

        <div className="relative z-10 p-8 max-w-7xl mx-auto">
          {/* Hero Header */}
          <motion.div
            className="mb-10 text-center"
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-indigo-500/20 mb-6 text-xs text-indigo-400 font-medium">
              <span className="agent-dot running" />
              NEXUS OS v1.0 — Autonomous Engineering Active
            </div>
            <h1 className="text-5xl font-black mb-4 leading-tight">
              <span className="gradient-text">AI-Native Engineering</span>
              <br />
              <span className="text-gray-200">Operating System</span>
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              10 autonomous agents. Infinite engineering capacity. Transform requirements into
              production software — autonomously.
            </p>
          </motion.div>

          {/* Command Input */}
          <motion.div
            className="mb-10 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="glass-elevated rounded-2xl p-2 flex gap-2">
              <div className="flex-1 flex items-center gap-3 px-4">
                <Brain size={18} className="text-indigo-400 flex-shrink-0" />
                <input
                  type="text"
                  value={requirement}
                  onChange={(e) => setRequirement(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleLaunch()}
                  placeholder="Describe what you want to build... (e.g., 'Build a SaaS analytics dashboard with real-time charts')"
                  className="flex-1 bg-transparent text-gray-200 placeholder-gray-600 text-sm outline-none"
                />
              </div>
              <motion.button
                onClick={handleLaunch}
                disabled={isLaunching || !requirement.trim()}
                className="btn-primary flex items-center gap-2 rounded-xl disabled:opacity-40"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isLaunching ? (
                  <motion.div
                    className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                  />
                ) : (
                  <Play size={14} />
                )}
                {isLaunching ? "Launching..." : "Launch Pipeline"}
                {!isLaunching && <ArrowRight size={14} />}
              </motion.button>
            </div>
            <p className="text-center text-xs text-gray-700 mt-2">
              Powered by 10 autonomous agents · GPT-4o · LangGraph orchestration
            </p>
          </motion.div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {STATS.map((stat, i) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  className="nexus-card p-5"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * i }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <Icon size={16} style={{ color: stat.color }} />
                    <span className="text-[10px] text-emerald-400 font-medium">{stat.delta}</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-100 mb-1">{stat.value}</div>
                  <div className="text-xs text-gray-500">{stat.label}</div>
                  <div className="progress-bar mt-3">
                    <motion.div
                      className="progress-fill"
                      initial={{ width: 0 }}
                      animate={{ width: "70%" }}
                      transition={{ delay: 0.5 + i * 0.1, duration: 0.8 }}
                    />
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Agents Grid + Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Agents Panel */}
            <motion.div
              className="lg:col-span-2 nexus-card p-6"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <div className="flex items-center justify-between mb-5">
                <h2 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
                  <Cpu size={16} className="text-indigo-400" />
                  Engineering Agent Fleet
                </h2>
                <span className="status-badge operational">10 agents ready</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {AGENT_STATUS.map((agent) => (
                  <AgentCard key={agent.name} agent={agent} />
                ))}
              </div>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              className="nexus-card p-6"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h2 className="text-sm font-semibold text-gray-200 mb-5 flex items-center gap-2">
                <Zap size={16} className="text-amber-400" />
                Quick Actions
              </h2>
              <div className="flex flex-col gap-3">
                {[
                  { label: "Parse Requirements",  href: "/requirements", icon: Brain,      color: "#8b5cf6" },
                  { label: "Run Debug Session",    href: "/debug",        icon: Bug,        color: "#fb923c" },
                  { label: "Deploy Application",   href: "/deployments",  icon: Rocket,     color: "#f59e0b" },
                  { label: "View Repositories",    href: "/repositories", icon: GitBranch,  color: "#10b981" },
                  { label: "Monitor Systems",      href: "/monitoring",   icon: Activity,   color: "#a78bfa" },
                ].map((action) => {
                  const Icon = action.icon;
                  return (
                    <Link key={action.href} href={action.href}>
                      <motion.div
                        className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer group"
                        whileHover={{ x: 4 }}
                      >
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                          style={{ background: `${action.color}15` }}
                        >
                          <Icon size={15} style={{ color: action.color }} />
                        </div>
                        <span className="text-sm text-gray-300 group-hover:text-gray-100 transition-colors">
                          {action.label}
                        </span>
                        <ArrowRight size={14} className="ml-auto text-gray-700 group-hover:text-gray-400 transition-colors" />
                      </motion.div>
                    </Link>
                  );
                })}
              </div>
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  );
}

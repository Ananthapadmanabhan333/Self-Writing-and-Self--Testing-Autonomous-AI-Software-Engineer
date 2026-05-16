"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Cpu, GitBranch, Rocket, Bug, TestTube, Server,
  Brain, Network, BarChart3, Shield, Settings, Zap,
} from "lucide-react";

const NAV_ITEMS = [
  { icon: Zap,        label: "Control Center",   href: "/",            color: "#6366f1" },
  { icon: Brain,      label: "Requirements",      href: "/requirements", color: "#8b5cf6" },
  { icon: Cpu,        label: "Engineering",        href: "/engineering",  color: "#06b6d4" },
  { icon: GitBranch,  label: "Repositories",       href: "/repositories", color: "#10b981" },
  { icon: Bug,        label: "Debugger",           href: "/debug",        color: "#fb923c" },
  { icon: TestTube,   label: "Testing & QA",       href: "/testing",      color: "#34d399" },
  { icon: Rocket,     label: "Deployments",         href: "/deployments",  color: "#f59e0b" },
  { icon: Server,     label: "Infrastructure",      href: "/infra",        color: "#60a5fa" },
  { icon: BarChart3,  label: "Monitoring",          href: "/monitoring",   color: "#a78bfa" },
  { icon: Network,    label: "Knowledge Graph",     href: "/knowledge",    color: "#f43f5e" },
  { icon: Shield,     label: "Security",            href: "/security",     color: "#ef4444" },
  { icon: Settings,   label: "Settings",            href: "/settings",     color: "#6b7280" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <motion.div
        className="mb-6 relative"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 200 }}
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center animate-glow-pulse">
          <Zap size={18} className="text-white" />
        </div>
      </motion.div>

      {/* Nav Items */}
      <nav className="flex flex-col gap-1 flex-1 w-full px-2">
        {NAV_ITEMS.map((item, i) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <Link href={item.href} title={item.label}>
                <div
                  className={`relative w-full flex items-center justify-center h-10 rounded-xl transition-all duration-200 group cursor-pointer ${
                    isActive
                      ? "bg-indigo-500/20 border border-indigo-500/40"
                      : "hover:bg-white/5"
                  }`}
                >
                  <Icon
                    size={18}
                    style={{ color: isActive ? item.color : "#4a5568" }}
                    className="transition-colors duration-200 group-hover:text-white"
                  />
                  {isActive && (
                    <motion.div
                      layoutId="sidebar-active"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r"
                      style={{ background: item.color }}
                    />
                  )}
                  {/* Tooltip */}
                  <div className="absolute left-full ml-3 px-2 py-1 bg-gray-900 border border-gray-700 rounded-md text-xs text-gray-200 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                    {item.label}
                  </div>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </nav>

      {/* Bottom status dot */}
      <div className="mt-4 flex flex-col items-center gap-1">
        <div className="agent-dot running" />
        <span className="text-[9px] text-gray-600 uppercase tracking-wider">live</span>
      </div>
    </aside>
  );
}

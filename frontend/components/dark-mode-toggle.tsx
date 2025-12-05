"use client";

import { useEffect, useState } from "react";
import { MoonIcon, SunIcon } from "@phosphor-icons/react";
import { THEME_STORAGE_KEY, cn } from "@/lib/utils";

const THEME_SCRIPT = `
  (function() {
    const doc = document.documentElement;
    const theme = localStorage.getItem("${THEME_STORAGE_KEY}") ?? "dark";
    doc.classList.remove("dark", "light");
    doc.classList.add(theme);
  })();
`
  .trim()
  .replace(/\n/g, "")
  .replace(/\s+/g, " ");

function applyTheme(theme: "dark" | "light") {
  const doc = document.documentElement;
  doc.classList.remove("dark", "light");
  doc.classList.add(theme);
  localStorage.setItem(THEME_STORAGE_KEY, theme);
}

interface DarkModeToggleProps {
  className?: string;
}

export function ApplyDarkModeScript() {
  return <script id="dark-mode-script">{THEME_SCRIPT}</script>;
}

export function DarkModeToggle({ className }: DarkModeToggleProps) {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const storedTheme = (localStorage.getItem(THEME_STORAGE_KEY) as "dark" | "light") ?? "dark";
    setTheme(storedTheme);
    applyTheme(storedTheme);
  }, []);

  function toggleTheme() {
    const newTheme = theme === "dark" ? "light" : "dark";
    applyTheme(newTheme);
    setTheme(newTheme);
  }

  if (!mounted) {
    return null;
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={cn(
        "fixed top-6 right-6 z-50 flex items-center justify-center rounded-full border bg-background p-2 shadow-md transition-all hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
        className,
      )}
      aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
    >
      {theme === "dark" ? (
        <SunIcon size={20} weight="bold" className="text-foreground" />
      ) : (
        <MoonIcon size={20} weight="bold" className="text-foreground" />
      )}
    </button>
  );
}


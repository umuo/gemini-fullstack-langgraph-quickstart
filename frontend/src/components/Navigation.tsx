import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

export function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: "/", label: "试卷生成", description: "智能试卷制作工具" },
    { path: "/research", label: "研究助手", description: "AI驱动的深度研究" }
  ];

  return (
    <nav className="border-b border-neutral-700 bg-neutral-900/95 backdrop-blur">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">DR</span>
              </div>
              <span className="font-bold text-xl text-neutral-100">DeepResearcher</span>
            </Link>
            
            <div className="flex space-x-6">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "flex flex-col items-start px-3 py-2 rounded-md text-sm transition-colors",
                    (location.pathname === item.path || 
                     (item.path === "/" && location.pathname === "/exam"))
                      ? "bg-neutral-700 text-neutral-100"
                      : "text-neutral-400 hover:text-neutral-100 hover:bg-neutral-700/50"
                  )}
                >
                  <span className="font-medium">{item.label}</span>
                  <span className="text-xs opacity-70">{item.description}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
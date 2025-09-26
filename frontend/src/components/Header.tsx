import React from "react";
import { Link } from "@tanstack/react-router";
import { Button } from "./ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "./ui/sheet";
import {
  Home,
  Users,
  BookOpen,
  X,
  Menu,
} from "lucide-react";

interface NavItemProps {
  children: React.ReactNode;
  to?: string;
  href?: string;
}

function NavItem({ children, to, href }: NavItemProps) {
  if (to) {
    return (
      <li>
        <Link
          to={to}
          className="flex items-center gap-2 font-medium text-current hover:text-primary transition-colors"
        >
          {children}
        </Link>
      </li>
    );
  }

  return (
    <li>
      <a
        href={href || "#"}
        target={href ? "_blank" : "_self"}
        className="flex items-center gap-2 font-medium text-current hover:text-primary transition-colors"
      >
        {children}
      </a>
    </li>
  );
}

const NAV_MENU = [
  {
    name: "Home",
    icon: Home,
    to: "/",
  },
  {
    name: "Team",
    icon: Users,
    to: "/team",
  },
  {
    name: "Learn",
    icon: BookOpen,
    to: "/learn",
  },
];

export function Navbar() {
  const [open, setOpen] = React.useState(false);
  const [isScrolling, setIsScrolling] = React.useState(false);

  React.useEffect(() => {
    window.addEventListener(
      "resize",
      () => window.innerWidth >= 960 && setOpen(false)
    );
  }, []);

  React.useEffect(() => {
    function handleScroll() {
      if (window.scrollY > 0) {
        setIsScrolling(true);
      } else {
        setIsScrolling(false);
      }
    }

    window.addEventListener("scroll", handleScroll);

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 w-full border-b transition-colors duration-200 ${isScrolling
        ? "bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
        : "bg-transparent border-transparent"
        }`}
    >
      <div className="container mx-auto flex items-center justify-between px-4 py-3">
        <h1 className={`text-lg font-bold transition-colors ${isScrolling ? "text-foreground" : "text-foreground"
          }`}>
          AI4SIDS
        </h1>

        <ul className={`ml-10 hidden items-center gap-6 lg:flex transition-colors ${isScrolling ? "text-foreground" : "text-foreground"
          }`}>
          {NAV_MENU.map(({ name, icon: Icon, to }) => (
            <NavItem key={name} to={to}>
              <Icon className="h-5 w-5" />
              <span>{name}</span>
            </NavItem>
          ))}
        </ul>

        <div className="hidden items-center gap-4 lg:flex">
          <Button
            variant={isScrolling ? "outline" : "outline"}
          >
            Log in
          </Button>
        </div>

        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="ml-auto lg:hidden"
            >
              {open ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-[300px] sm:w-[400px]">
            <div className="flex flex-col gap-4 py-4">
              <ul className="flex flex-col gap-4">
                {NAV_MENU.map(({ name, icon: Icon, to }) => (
                  <NavItem key={name} to={to}>
                    <Icon className="h-5 w-5" />
                    {name}
                  </NavItem>
                ))}
              </ul>
              <div className="mt-6 flex flex-col items-stretch gap-4">
                <Button variant="outline" className="w-full">
                  Log in
                </Button>
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}

export default Navbar;

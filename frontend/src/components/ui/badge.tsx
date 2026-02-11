import * as React from "react"
import { cn } from "@/lib/utils"

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: "default" | "outline"
    size?: "default" | "sm"
}

function Badge({
    className,
    variant = "default",
    size = "default",
    ...props
}: BadgeProps) {
    return (
        <div
            className={cn(
                "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                variant === "default" && "bg-primary text-primary-foreground hover:bg-primary/80",
                variant === "outline" && "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
                size === "sm" && "px-1.5 py-0.5 text-xs",
                className
            )}
            {...props}
        />
    )
}

export { Badge }
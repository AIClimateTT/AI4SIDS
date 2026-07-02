import { ArrowDown, ArrowUp, ChevronsUpDown, EyeOff } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import type { DataTableColumnHeaderProps } from "./types"

/**
 * Sortable column header with dropdown menu
 *
 * Supports server-side sorting by calling onStateChange with sort params
 */
export function DataTableColumnHeader<TData, TValue>({
  column,
  title,
  sorting,
  onStateChange,
  enableSorting = true,
  className,
}: DataTableColumnHeaderProps<TData, TValue>) {
  // If sorting is disabled or no onStateChange, render plain header
  if (!enableSorting || !onStateChange) {
    return <div className={cn(className)}>{title}</div>
  }

  // Determine current sort state for this column
  const columnId = column.id
  const isSorted = sorting?.sortBy === columnId
  const sortDirection = isSorted ? sorting?.sortOrder : undefined

  const handleSort = (direction: "asc" | "desc") => {
    if (isSorted && sortDirection === direction) {
      // Clear sort if clicking the same direction
      onStateChange({ sort_by: undefined, sort_order: undefined, page: 1 })
    } else {
      onStateChange({ sort_by: columnId, sort_order: direction, page: 1 })
    }
  }

  const handleHide = () => {
    column.toggleVisibility(false)
  }

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="-ml-3 h-8 data-[state=open]:bg-accent"
          >
            <span>{title}</span>
            {sortDirection === "desc" ? (
              <ArrowDown className="ml-2 h-4 w-4" />
            ) : sortDirection === "asc" ? (
              <ArrowUp className="ml-2 h-4 w-4" />
            ) : (
              <ChevronsUpDown className="ml-2 h-4 w-4" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem onClick={() => handleSort("asc")}>
            <ArrowUp className="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
            Asc
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => handleSort("desc")}>
            <ArrowDown className="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
            Desc
          </DropdownMenuItem>
          {column.getCanHide() && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleHide}>
                <EyeOff className="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
                Hide
              </DropdownMenuItem>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

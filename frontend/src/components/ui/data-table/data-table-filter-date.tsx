import * as React from "react"
import { format } from "date-fns"
import { Calendar as CalendarIcon, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import type { DateFilterConfig } from "./types"
import type { DateRange } from "react-day-picker"

interface DataTableFilterDateProps {
  filter: DateFilterConfig
  values: Record<string, string | undefined>
  onChange: (updates: Record<string, string | undefined>) => void
}

function parseDateOnly(value: string | undefined): Date | undefined {
  if (!value) return undefined

  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (!match) {
    const date = new Date(value)
    return Number.isNaN(date.getTime()) ? undefined : date
  }

  const [, year, month, day] = match
  return new Date(Number(year), Number(month) - 1, Number(day))
}

/**
 * Date filter with single/range mode toggle
 *
 * Single mode: uses filter.key (e.g., 'date')
 * Range mode: uses filter.key + '_from' and filter.key + '_to' (e.g., 'date_from', 'date_to')
 */
export function DataTableFilterDate({
  filter,
  values,
  onChange,
}: DataTableFilterDateProps) {
  const allowRange = filter.allowRange ?? true
  const defaultMode = filter.defaultMode ?? "single"

  // Determine current mode based on URL values
  const fromKey = `${filter.key}_from`
  const toKey = `${filter.key}_to`
  const hasRangeValues = values[fromKey] || values[toKey]
  const hasSingleValue = values[filter.key]

  const [mode, setMode] = React.useState<"single" | "range">(() => {
    if (hasRangeValues) return "range"
    if (hasSingleValue) return "single"
    return defaultMode
  })

  // Parse current values
  const singleDate = parseDateOnly(values[filter.key])

  const dateRange: DateRange | undefined =
    values[fromKey] || values[toKey]
      ? {
          from: parseDateOnly(values[fromKey]),
          to: parseDateOnly(values[toKey]),
        }
      : undefined

  // Handle mode change
  const handleModeChange = (newMode: "single" | "range") => {
    if (newMode === mode) return

    setMode(newMode)

    // Clear values when switching modes
    if (newMode === "single") {
      onChange({
        [fromKey]: undefined,
        [toKey]: undefined,
      })
    } else {
      onChange({
        [filter.key]: undefined,
      })
    }
  }

  // Handle single date selection
  const handleSingleDateSelect = (date: Date | undefined) => {
    onChange({
      [filter.key]: date ? format(date, "yyyy-MM-dd") : undefined,
    })
  }

  // Handle date range selection
  const handleRangeSelect = (range: DateRange | undefined) => {
    onChange({
      [fromKey]: range?.from ? format(range.from, "yyyy-MM-dd") : undefined,
      [toKey]: range?.to ? format(range.to, "yyyy-MM-dd") : undefined,
    })
  }

  // Clear all date values
  const handleClear = () => {
    onChange({
      [filter.key]: undefined,
      [fromKey]: undefined,
      [toKey]: undefined,
    })
  }

  // Check if any date is selected
  const hasValue =
    mode === "single" ? !!singleDate : !!(dateRange?.from || dateRange?.to)

  // Format display text
  const getDisplayText = () => {
    if (mode === "single") {
      return singleDate ? format(singleDate, "MMM d, yyyy") : filter.label
    }
    if (dateRange?.from) {
      if (dateRange.to) {
        return `${format(dateRange.from, "MMM d")} - ${format(dateRange.to, "MMM d, yyyy")}`
      }
      return `${format(dateRange.from, "MMM d, yyyy")} - ...`
    }
    return filter.label
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={cn(
            "h-9 justify-start text-left font-normal",
            !hasValue && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          <span className="truncate">{getDisplayText()}</span>
          {hasValue && (
            <X
              className="ml-2 h-4 w-4 shrink-0 opacity-50 hover:opacity-100"
              onClick={(e) => {
                e.stopPropagation()
                handleClear()
              }}
            />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="space-y-3 p-3">
          {/* Mode toggle */}
          {allowRange && (
            <ToggleGroup
              type="single"
              value={mode}
              onValueChange={(value) => {
                if (value) handleModeChange(value as "single" | "range")
              }}
              className="justify-start"
            >
              <ToggleGroupItem value="single" size="sm">
                Single
              </ToggleGroupItem>
              <ToggleGroupItem value="range" size="sm">
                Range
              </ToggleGroupItem>
            </ToggleGroup>
          )}

          {/* Calendar(s) */}
          {mode === "single" ? (
            <Calendar
              mode="single"
              selected={singleDate}
              onSelect={handleSingleDateSelect}
            />
          ) : (
            <Calendar
              mode="range"
              selected={dateRange}
              onSelect={handleRangeSelect}
              numberOfMonths={2}
            />
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}

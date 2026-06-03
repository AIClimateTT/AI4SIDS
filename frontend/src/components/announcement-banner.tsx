import { Banner } from "@/components/ui/banner"

function BannerNewFeature() {
  return (
    <Banner variant="muted" className="dark text-foreground">
      <div className="w-full">
        <p className="flex justify-center text-sm">
          <span className="me-1 text-base leading-none">🚧</span>
          AI4SIDS is a beta version for testing only.
        </p>
      </div>
    </Banner>
  )
}

export { BannerNewFeature }
import { MichiganLoader } from '@/components/MichiganLoader'

export default function Loading() {
  return (
    <div 
      className="flex items-center justify-center min-h-screen w-full"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      <div className="text-center">
        <MichiganLoader size={150} />
        <p 
          className="mt-6 text-lg font-medium"
          style={{ color: 'var(--color-foreground)' }}
        >
          Loading dashboard...
        </p>
      </div>
    </div>
  )
}


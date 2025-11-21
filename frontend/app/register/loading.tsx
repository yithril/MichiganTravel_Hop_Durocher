import { MichiganLoader } from '@/components/MichiganLoader'

export default function Loading() {
  return (
    <div 
      className="flex items-center justify-center min-h-screen w-full"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      <MichiganLoader size={150} />
    </div>
  )
}


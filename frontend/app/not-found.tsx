import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">404</h1>
        <h2 className="mt-2 text-2xl font-semibold">Page Not Found</h2>
        <p className="mt-2 text-muted-foreground">
          The page you are looking for does not exist.
        </p>
        <Link
          href="/"
          className="mt-4 inline-block rounded bg-primary px-4 py-2 text-primary-foreground"
        >
          Go back home
        </Link>
      </div>
    </div>
  )
}


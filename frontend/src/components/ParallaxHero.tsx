'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function ParallaxHero() {
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const getParallaxOffset = (sectionIndex: number) => {
    const sectionHeight = typeof window !== 'undefined' ? window.innerHeight : 0
    const offset = scrollY - sectionHeight * sectionIndex
    return Math.max(0, offset * 0.5)
  }

  return (
    <div className="relative">
      {/* First Section */}
      <section className="relative h-screen overflow-hidden">
        <div 
          className="absolute inset-0"
          style={{
            transform: `translateY(${getParallaxOffset(0)}px)`,
          }}
        >
          <Image
            src="/img/front_page_1.jpg"
            alt="Michigan Landscape"
            fill
            className="object-cover"
            priority
          />
        </div>
        {/* Bouncing Arrow */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <svg
            className="w-8 h-8 text-white"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
          </svg>
        </div>
      </section>

      {/* Second Section - Glacier Image with Hidden Gems Text Right */}
      <section className="relative h-screen overflow-hidden">
        <div 
          className="absolute inset-0"
          style={{
            transform: `translateY(${getParallaxOffset(1)}px)`,
          }}
        >
          <Image
            src="/img/glacier.jpeg"
            alt="Michigan Glacier"
            fill
            className="object-cover"
          />
        </div>
        <div className="absolute inset-0 flex items-center">
          <div className="container mx-auto px-4 flex justify-end">
            <div className="max-w-md text-right" style={{ color: 'var(--color-michigan-dark)' }}>
              <span className="inline-block mb-2 font-light tracking-wider font-accent" style={{ color: 'var(--color-michigan-dark)' }}>
                HIDDEN GEM
              </span>
              <h2 className="text-4xl md:text-5xl font-bold mb-4 font-heading" style={{ color: 'var(--color-michigan-dark)' }}>
                Hidden Gems
              </h2>
              <p className="text-lg md:text-xl" style={{ color: 'var(--color-michigan-dark)' }}>
                Explore the breathtaking landscapes and hidden treasures that make Michigan truly special.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Third Section - Text Left */}
      <section className="relative h-screen overflow-hidden">
        <div 
          className="absolute inset-0"
          style={{
            transform: `translateY(${getParallaxOffset(2)}px)`,
          }}
        >
          <Image
            src="/img/front_page_2.jpg"
            alt="Michigan Landscape"
            fill
            className="object-cover"
          />
        </div>
        <div className="absolute inset-0 bg-overlay-dark-light flex items-center">
          <div className="container mx-auto px-4">
            <div className="max-w-md text-white">
              <span className="inline-block mb-2 font-light tracking-wider font-accent" style={{ color: 'var(--color-primary)' }}>
                HIDDEN GEM
              </span>
              <h2 className="text-4xl md:text-5xl font-bold mb-4 font-heading">
                Discover the Unseen
              </h2>
              <p className="text-lg md:text-xl">
                Explore the breathtaking landscapes and hidden treasures that make Michigan truly special.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Fourth Section - Text Right */}
      <section className="relative h-screen overflow-hidden">
        <div 
          className="absolute inset-0"
          style={{
            transform: `translateY(${getParallaxOffset(3)}px)`,
          }}
        >
          <Image
            src="/img/front_page_3.jpg"
            alt="Michigan Landscape"
            fill
            className="object-cover"
          />
        </div>
        <div className="absolute inset-0 bg-overlay-dark-light flex items-center">
          <div className="container mx-auto px-4 flex justify-end">
            <div className="max-w-md text-white text-right">
              <span className="inline-block mb-2 font-light tracking-wider font-accent" style={{ color: 'var(--color-primary)' }}>
                OUTDOORSY
              </span>
              <h2 className="text-4xl md:text-5xl font-bold mb-4 font-heading">
                Natural Beauty
              </h2>
              <p className="text-lg md:text-xl">
                From pristine lakeshores to rolling hills, discover the diverse beauty that awaits you.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Fifth Section - Text Left */}
      <section className="relative h-screen overflow-hidden">
        <div 
          className="absolute inset-0"
          style={{
            transform: `translateY(${getParallaxOffset(4)}px)`,
          }}
        >
          <Image
            src="/img/front_page_4.jpg"
            alt="Michigan Landscape"
            fill
            className="object-cover"
          />
        </div>
        <div className="absolute inset-0 bg-overlay-dark-light flex items-center">
          <div className="container mx-auto px-4">
            <div className="max-w-md text-white">
              <span className="inline-block mb-2 font-light tracking-wider font-accent" style={{ color: 'var(--color-primary)' }}>
                RUSTIC
              </span>
              <h2 className="text-4xl md:text-5xl font-bold mb-4 font-heading">
                Your Adventure Awaits
              </h2>
              <p className="text-lg md:text-xl">
                Join us and uncover the stories, places, and experiences that define Michigan.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(to bottom, var(--color-michigan-dark), black)' }}>
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 font-heading">
            Ready to Explore?
          </h2>
          <p className="text-xl md:text-2xl mb-12 max-w-2xl mx-auto" style={{ color: 'var(--color-muted)' }}>
            Experience a side of Michigan you haven't seen before. Register or login to get started.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/register"
              className="rounded-lg px-8 py-4 text-lg font-semibold transition-colors font-heading"
              style={{ 
                backgroundColor: 'var(--color-primary)',
                color: 'var(--color-michigan-dark)'
              }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
            >
              Register
            </Link>
            <Link
              href="/login"
              className="rounded-lg border-2 px-8 py-4 text-lg font-semibold transition-colors font-heading"
              style={{ 
                borderColor: 'var(--color-primary)',
                color: 'var(--color-primary)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-primary)'
                e.currentTarget.style.color = 'var(--color-michigan-dark)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.color = 'var(--color-primary)'
              }}
            >
              Login
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}


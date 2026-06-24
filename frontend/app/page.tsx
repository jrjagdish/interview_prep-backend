import Navbar from '@/components/landing/Navbar'
import Hero from '@/components/landing/Hero'
import Features from '@/components/landing/Features'
import HowItWorks from '@/components/landing/HowItWorks'
import InterviewTypes from '@/components/landing/InterviewTypes'
import Pricing from '@/components/landing/Pricing'
import Testimonials from '@/components/landing/Testimonials'
import Footer from '@/components/landing/Footer'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 overflow-x-hidden dark:bg-[#07090f] dark:text-white">
      <Navbar />
      <Hero />
      <Features />
      <InterviewTypes />
      <HowItWorks />
      <Pricing />
      <Testimonials />
      <Footer />
    </div>
  )
}

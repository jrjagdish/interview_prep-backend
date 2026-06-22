'use client'

export default function UserAvatar() {
  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md shadow-xl">
      {/* Avatar circle */}
      <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shrink-0 shadow-md">
        <span className="text-white font-bold text-sm select-none">U</span>
        {/* Online dot */}
        <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[#07090f]" />
      </div>

      {/* Name + role */}
      <div className="flex flex-col leading-tight">
        <span className="text-white text-sm font-semibold">You</span>
        <span className="text-white/40 text-xs">Candidate</span>
      </div>

      {/* Mic icon to show user is live */}
      <div className="ml-1 text-white/30">
        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm6.364 9.05a.75.75 0 0 1 .728.96A7.5 7.5 0 0 1 12.75 17.44v2.31h2.5a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1 0-1.5h2.5v-2.31A7.5 7.5 0 0 1 4.908 11.01a.75.75 0 1 1 1.455-.36A6 6 0 0 0 18 11a.75.75 0 0 1 .364-.95z" />
        </svg>
      </div>
    </div>
  )
}

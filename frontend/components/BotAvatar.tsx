'use client'

interface BotAvatarProps {
  isSpeaking: boolean
}

export default function BotAvatar({ isSpeaking }: BotAvatarProps) {
  return (
    <div className="relative flex items-center justify-center">

      {/* Wave rings — only visible while bot is speaking */}
      {isSpeaking && (
        <>
          <span className="absolute inline-flex h-full w-full rounded-full bg-indigo-500 opacity-0 animate-wave-ring" />
          <span className="absolute inline-flex h-full w-full rounded-full bg-indigo-500 opacity-0 animate-wave-ring-2" />
          <span className="absolute inline-flex h-full w-full rounded-full bg-indigo-500 opacity-0 animate-wave-ring-3" />
        </>
      )}

      {/* Outer glow ring — always visible, pulses when speaking */}
      <div
        className={`
          absolute inset-0 rounded-full transition-all duration-500
          ${isSpeaking
            ? 'shadow-[0_0_50px_15px_rgba(99,102,241,0.55)] scale-105'
            : 'shadow-[0_0_20px_4px_rgba(99,102,241,0.25)]'}
        `}
      />

      {/* Bot icon circle */}
      <div
        className={`
          relative z-10 w-40 h-40 rounded-full flex items-center justify-center
          bg-gradient-to-br from-indigo-500 via-violet-600 to-purple-700
          ${isSpeaking ? 'animate-pulse-glow' : 'animate-breathe'}
          transition-all duration-300
        `}
      >
        {/* Bot face SVG */}
        <svg
          viewBox="0 0 100 100"
          className="w-20 h-20 drop-shadow-lg"
          aria-label="AI Bot"
        >
          {/* Antenna */}
          <line x1="50" y1="2" x2="50" y2="18" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
          <circle cx="50" cy="2" r="3.5" fill="white" />

          {/* Head */}
          <rect x="18" y="18" width="64" height="58" rx="14" fill="white" fillOpacity="0.15" />

          {/* Eyes */}
          <circle cx="36" cy="40" r="9" fill="white" fillOpacity="0.9" />
          <circle cx="64" cy="40" r="9" fill="white" fillOpacity="0.9" />
          {/* Pupils — shift slightly when speaking to look "alive" */}
          <circle
            cx={isSpeaking ? 38 : 37}
            cy={isSpeaking ? 41 : 42}
            r="4.5"
            fill="#3730a3"
            className="transition-all duration-200"
          />
          <circle
            cx={isSpeaking ? 66 : 65}
            cy={isSpeaking ? 41 : 42}
            r="4.5"
            fill="#3730a3"
            className="transition-all duration-200"
          />
          {/* Eye shine */}
          <circle cx="39" cy="38" r="1.8" fill="white" fillOpacity="0.8" />
          <circle cx="67" cy="38" r="1.8" fill="white" fillOpacity="0.8" />

          {/* Mouth — changes shape when speaking */}
          {isSpeaking ? (
            <ellipse cx="50" cy="66" rx="12" ry="6" fill="white" fillOpacity="0.85" />
          ) : (
            <path
              d="M 36 64 Q 50 74 64 64"
              stroke="white"
              strokeWidth="3"
              fill="none"
              strokeLinecap="round"
              strokeOpacity="0.85"
            />
          )}

          {/* Sound bars inside mouth area when speaking */}
          {isSpeaking && (
            <>
              <rect x="44" y="62" width="3" height="8" rx="1.5" fill="#3730a3" opacity="0.7" />
              <rect x="49" y="60" width="3" height="12" rx="1.5" fill="#3730a3" opacity="0.7" />
              <rect x="54" y="63" width="3" height="6" rx="1.5" fill="#3730a3" opacity="0.7" />
            </>
          )}

          {/* Ear nubs */}
          <rect x="10" y="36" width="8" height="16" rx="4" fill="white" fillOpacity="0.4" />
          <rect x="82" y="36" width="8" height="16" rx="4" fill="white" fillOpacity="0.4" />
        </svg>
      </div>
    </div>
  )
}

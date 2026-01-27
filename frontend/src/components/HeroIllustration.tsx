import React from 'react';

const HeroIllustration: React.FC = () => {
  return (
    <div className="hero-container">
      <style>{`
        .hero-container {
          width: 100%;
          height: 100%;
          min-height: 100vh;
          background-color: #050814;
          background-image: 
            radial-gradient(circle at 10% 20%, rgba(0, 255, 200, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(114, 9, 183, 0.08) 0%, transparent 40%);
          position: relative;
          overflow: hidden;
          display: flex;
          justify-content: center;
          align-items: center;
          padding: clamp(1rem, 3vw, 4rem);
        }

        .hero-svg-wrapper {
          width: 100%;
          max-width: min(90vw, 1000px);
          height: auto;
          filter: drop-shadow(0 20px 50px rgba(0,0,0,0.3));
          animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
          100% { transform: translateY(0px); }
        }
        
        @keyframes pulse-glow {
          0% { opacity: 0.5; }
          50% { opacity: 1; }
          100% { opacity: 0.5; }
        }

        .neon-text {
          animation: pulse-glow 3s infinite;
        }

        /* Full HD (1920x1080) - Otimizado */
        @media (min-width: 1920px) {
          .hero-svg-wrapper {
            max-width: 1200px;
          }
        }

        /* Desktop padrão (1366px - 1920px) */
        @media (min-width: 1366px) and (max-width: 1919px) {
          .hero-svg-wrapper {
            max-width: 900px;
          }
        }

        /* Laptops (1024px - 1365px) */
        @media (min-width: 1024px) and (max-width: 1365px) {
          .hero-container {
            padding: clamp(1.5rem, 3vw, 3rem);
          }
          
          .hero-svg-wrapper {
            max-width: 700px;
          }
        }

        /* Tablets (768px - 1023px) */
        @media (min-width: 768px) and (max-width: 1023px) {
          .hero-container {
            padding: 2rem 1.5rem;
          }
          
          .hero-svg-wrapper {
            max-width: 600px;
          }
        }

        /* Mobile (até 767px) */
        @media (max-width: 767px) {
          .hero-container {
            min-height: auto;
            padding: 1.5rem 1rem;
          }
          
          .hero-svg-wrapper {
            max-width: 100%;
            filter: drop-shadow(0 10px 30px rgba(0,0,0,0.3));
          }
        }

        /* Mobile pequeno (até 480px) */
        @media (max-width: 480px) {
          .hero-container {
            padding: 1rem 0.5rem;
          }
        }

        /* Landscape em mobile */
        @media (max-height: 600px) and (orientation: landscape) {
          .hero-container {
            min-height: auto;
            padding: 1rem;
          }
          
          @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
          }
        }

        /* Monitores ultrawide */
        @media (min-width: 2560px) {
          .hero-svg-wrapper {
            max-width: 1400px;
          }
        }

        /* 4K */
        @media (min-width: 3840px) {
          .hero-svg-wrapper {
            max-width: 1800px;
          }
        }
      `}</style>

      <div className="hero-svg-wrapper">
        <svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
          <defs>
            {/* Gradients */}
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0f172a" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#1e293b" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="tealGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00ffc8" />
              <stop offset="100%" stopColor="#00b4d8" />
            </linearGradient>
            <linearGradient id="purpleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#7209b7" />
              <stop offset="100%" stopColor="#f72585" />
            </linearGradient>
            <linearGradient id="glassGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(255,255,255,0.1)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0.02)" />
            </linearGradient>
            
            {/* Glow Filter */}
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background Grid */}
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0, 255, 200, 0.05)" strokeWidth="1"/>
          </pattern>
          <rect width="800" height="500" fill="url(#grid)" />

          {/* Main Dashboard Panel */}
          <g transform="translate(100, 80)">
            {/* Panel Background with Glassmorphism */}
            <rect width="600" height="360" rx="16" fill="url(#bgGradient)" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
            <rect width="600" height="360" rx="16" fill="url(#glassGradient)" />
            
            {/* Header Bar */}
            <path d="M 0 16 Q 0 0 16 0 L 584 0 Q 600 0 600 16 L 600 50 L 0 50 Z" fill="rgba(0,0,0,0.2)" />
            <circle cx="30" cy="25" r="6" fill="#ef4444" opacity="0.8" />
            <circle cx="50" cy="25" r="6" fill="#f59e0b" opacity="0.8" />
            <circle cx="70" cy="25" r="6" fill="#22c55e" opacity="0.8" />
            <text x="300" y="32" textAnchor="middle" fill="#94a3b8" fontFamily="sans-serif" fontSize="14" fontWeight="600">Império das Rifas - Admin</text>

            {/* Sidebar */}
            <rect x="0" y="50" width="120" height="310" fill="rgba(255,255,255,0.02)" />
            <g transform="translate(20, 80)">
               <rect width="80" height="10" rx="4" fill="rgba(255,255,255,0.1)" />
               <rect y="25" width="60" height="10" rx="4" fill="rgba(255,255,255,0.1)" />
               <rect y="50" width="70" height="10" rx="4" fill="rgba(255,255,255,0.1)" />
               
               {/* Active Item */}
               <rect y="85" width="80" height="30" rx="6" fill="rgba(0, 255, 200, 0.1)" />
               <rect x="10" y="95" width="60" height="10" rx="4" fill="#00ffc8" />
            </g>

            {/* Content Area - Raffle Grid */}
            <g transform="translate(150, 80)">
               <text x="0" y="0" fill="#fff" fontFamily="sans-serif" fontSize="18" fontWeight="bold">Sorteio #1284</text>
               <text x="0" y="25" fill="#94a3b8" fontFamily="sans-serif" fontSize="12">Prêmio: iPhone 15 Pro Max</text>
               
               {/* Grid of Numbers */}
               <g transform="translate(0, 50)">
                  {Array.from({ length: 12 }).map((_, i) => {
                      const col = i % 4;
                      const row = Math.floor(i / 4);
                      const isSelected = i === 5 || i === 6 || i === 9;
                      return (
                        <g key={i} transform={`translate(${col * 65}, ${row * 65})`}>
                           <rect width="55" height="55" rx="8" 
                                 fill={isSelected ? "url(#tealGradient)" : "rgba(255,255,255,0.05)"}
                                 stroke={isSelected ? "none" : "rgba(255,255,255,0.1)"} />
                           <text x="27.5" y="32" textAnchor="middle" dominantBaseline="middle" 
                                 fill={isSelected ? "#050814" : "#fff"} 
                                 fontFamily="sans-serif" fontWeight="bold" fontSize="14">
                                 {100 + i}
                           </text>
                        </g>
                      )
                  })}
               </g>
            </g>
            
            {/* Right Side Stats / Pix */}
            <g transform="translate(440, 80)">
               {/* Pix Card */}
               <rect width="130" height="160" rx="12" fill="rgba(0,0,0,0.3)" stroke="rgba(255,255,255,0.1)" />
               <g transform="translate(65, 40)">
                   {/* Pix Logo Simulation */}
                   <circle r="25" fill="none" stroke="#00ffc8" strokeWidth="2" />
                   <path d="M -10 -10 L 0 0 L 10 -10 M -10 10 L 0 0 L 10 10" stroke="#00ffc8" strokeWidth="2" fill="none" />
               </g>
               <text x="65" y="90" textAnchor="middle" fill="#fff" fontFamily="sans-serif" fontSize="14" fontWeight="bold">Pagamento</text>
               <text x="65" y="110" textAnchor="middle" fill="#00ffc8" fontFamily="sans-serif" fontSize="12">Via PIX</text>
               <rect x="25" y="125" width="80" height="20" rx="4" fill="url(#tealGradient)" />
               <text x="65" y="139" textAnchor="middle" fill="#050814" fontFamily="sans-serif" fontSize="10" fontWeight="bold">PAGAR</text>
            </g>
          </g>

          {/* Floating Elements */}
          
          {/* "Vai Ganhar" Badge */}
          <g transform="translate(620, 40)">
             <circle r="50" fill="url(#purpleGradient)" opacity="0.9" filter="url(#glow)">
                 <animate attributeName="r" values="50;52;50" dur="2s" repeatCount="indefinite" />
             </circle>
             <text x="0" y="5" textAnchor="middle" fill="#fff" fontFamily="sans-serif" fontSize="14" fontWeight="bold" transform="rotate(15)">
                VAI GANHAR!
             </text>
          </g>

          {/* Decorative Circles */}
          <circle cx="50" cy="400" r="30" fill="none" stroke="#7209b7" strokeWidth="2" opacity="0.5" />
          <circle cx="750" cy="100" r="20" fill="#00ffc8" opacity="0.2" />

        </svg>
      </div>
    </div>
  );
};

export default HeroIllustration;
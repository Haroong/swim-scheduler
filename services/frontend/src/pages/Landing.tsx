import HeroSection from '../components/hero/HeroSection';
import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div className="bg-slate-50">
      {/* Hero Section */}
      <HeroSection />

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-4">
              왜 오늘수영을 써야 할까요?
            </h2>
            <p className="text-lg text-slate-600">
              성남시 공공 수영장 정보를 가장 빠르고 편리하게
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-ocean-50 to-wave-50 rounded-2xl p-8 border border-ocean-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-14 h-14 bg-gradient-to-br from-ocean-500 to-wave-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-3">실시간 정보</h3>
              <p className="text-slate-600 leading-relaxed">
                성남시 공공 수영장의 자유수영 일정을 실시간으로 수집하여 제공합니다.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-wave-50 to-emerald-50 rounded-2xl p-8 border border-wave-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-14 h-14 bg-gradient-to-br from-wave-500 to-emerald-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-3">한눈에 보기</h3>
              <p className="text-slate-600 leading-relaxed">
                달력 뷰와 일별 뷰로 원하는 날짜의 수영장 일정을 쉽게 확인하세요.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl p-8 border border-emerald-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-3">정확한 데이터</h3>
              <p className="text-slate-600 leading-relaxed">
                공공기관 공지사항을 기반으로 정확한 운영 정보를 제공합니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Access Section */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-ocean-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
            <div className="grid grid-cols-1 lg:grid-cols-2">
              {/* Left Side - Info */}
              <div className="p-12 flex flex-col justify-center">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-ocean-100 text-ocean-700 rounded-full text-sm font-semibold mb-6 w-fit">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  빠른 시작
                </div>
                <h2 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-6">
                  지금 바로<br />
                  수영 일정을<br />
                  확인하세요
                </h2>
                <p className="text-lg text-slate-600 mb-8 leading-relaxed">
                  복잡한 공지사항을 찾아다닐 필요 없이,
                  오늘수영에서 한 번에 확인하세요.
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Link
                    to="/today"
                    className="group px-6 py-3.5 bg-gradient-to-r from-ocean-500 to-wave-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center gap-2"
                  >
                    오늘의 일정
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </Link>
                  <Link
                    to="/calendar"
                    className="px-6 py-3.5 bg-slate-100 text-slate-700 rounded-xl font-semibold hover:bg-slate-200 transition-all flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    달력 보기
                  </Link>
                </div>
              </div>

              {/* Right Side - Visual */}
              <div className="relative bg-gradient-to-br from-ocean-500 via-wave-500 to-emerald-500 p-12 flex items-center justify-center overflow-hidden">
                {/* Wave Pattern */}
                <div className="absolute inset-0 opacity-20">
                  <svg className="absolute bottom-0 w-full h-32" viewBox="0 0 1440 320" preserveAspectRatio="none">
                    <path fill="white" d="M0,160L48,144C96,128,192,96,288,101.3C384,107,480,149,576,154.7C672,160,768,128,864,122.7C960,117,1056,139,1152,138.7C1248,139,1344,117,1392,106.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" />
                  </svg>
                </div>

                {/* Icon Grid */}
                <div className="relative grid grid-cols-3 gap-6">
                  {[...Array(9)].map((_, i) => (
                    <div
                      key={i}
                      className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg hover:scale-110 transition-transform"
                      style={{ animationDelay: `${i * 0.1}s` }}
                    >
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                      </svg>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-6">
            더 이상 공지사항을 찾아다니지 마세요
          </h2>
          <p className="text-lg text-slate-600 mb-10">
            오늘수영이 성남시 모든 공공 수영장 정보를 한곳에 모았습니다
          </p>
          <Link
            to="/today"
            className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-ocean-600 via-ocean-500 to-wave-500 text-white rounded-2xl font-bold text-lg shadow-2xl hover:shadow-ocean-500/50 hover:scale-105 transition-all duration-300"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
            지금 시작하기
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-ocean-500 to-wave-500 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <span className="text-lg font-bold">오늘수영</span>
              </div>
              <p className="text-slate-400 text-sm leading-relaxed">
                성남시 공공 수영장 자유수영 정보를<br />
                한눈에 확인하세요
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="font-bold mb-4">바로가기</h3>
              <ul className="space-y-2">
                <li>
                  <Link to="/today" className="text-slate-400 hover:text-white transition-colors text-sm">
                    오늘의 일정
                  </Link>
                </li>
                <li>
                  <Link to="/calendar" className="text-slate-400 hover:text-white transition-colors text-sm">
                    달력 보기
                  </Link>
                </li>
                <li>
                  <Link to="/monthly" className="text-slate-400 hover:text-white transition-colors text-sm">
                    월별 일정
                  </Link>
                </li>
              </ul>
            </div>

            {/* Info */}
            <div>
              <h3 className="font-bold mb-4">안내</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                실제 운영 시간은 각 시설에 문의해주세요.<br />
                데이터는 공공기관 공지사항을 기반으로 수집됩니다.
              </p>
            </div>
          </div>

          {/* Copyright */}
          <div className="border-t border-slate-800 mt-10 pt-8 text-center">
            <p className="text-slate-500 text-sm">
              © 2026 오늘수영. All rights reserved.
            </p>
            <div className="mt-3 flex items-center justify-center gap-2 text-slate-500 text-sm">
              <span>Made by 조혜륜</span>
              <a href="https://github.com/haroong" target="_blank" rel="noopener noreferrer" className="hover:text-slate-300 transition-colors">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

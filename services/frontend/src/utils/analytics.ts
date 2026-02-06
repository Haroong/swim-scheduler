// Google Analytics 4 유틸리티

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void;
    dataLayer: unknown[];
  }
}

const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID;

// GA4 초기화
export function initGA() {
  if (!GA_MEASUREMENT_ID) {
    console.log('[GA] Measurement ID not configured');
    return;
  }

  // gtag.js 스크립트 로드
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);

  // gtag 초기화
  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag(...args: unknown[]) {
    window.dataLayer.push(args);
  };
  window.gtag('js', new Date());
  window.gtag('config', GA_MEASUREMENT_ID);

  console.log('[GA] Initialized');
}

// 페이지뷰 추적
export function trackPageView(path: string, title?: string) {
  if (!GA_MEASUREMENT_ID || !window.gtag) return;

  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: title,
  });
}

// ===== 커스텀 이벤트 =====

// 즐겨찾기 토글
export function trackFavoriteToggle(facilityId: number, facilityName: string, action: 'add' | 'remove') {
  if (!GA_MEASUREMENT_ID || !window.gtag) return;

  window.gtag('event', 'favorite_toggle', {
    facility_id: facilityId,
    facility_name: facilityName,
    action: action,
  });
}

// 시설 카드 확장 (상세 보기)
export function trackFacilityView(facilityId: number, facilityName: string) {
  if (!GA_MEASUREMENT_ID || !window.gtag) return;

  window.gtag('event', 'facility_view', {
    facility_id: facilityId,
    facility_name: facilityName,
  });
}

// 필터 사용
export function trackFilterUse(filterType: 'facility' | 'month' | 'date', value: string) {
  if (!GA_MEASUREMENT_ID || !window.gtag) return;

  window.gtag('event', 'filter_use', {
    filter_type: filterType,
    filter_value: value,
  });
}

// 외부 링크 클릭 (원본 공지)
export function trackOutboundLink(url: string, facilityName?: string) {
  if (!GA_MEASUREMENT_ID || !window.gtag) return;

  window.gtag('event', 'outbound_link', {
    url: url,
    facility_name: facilityName,
  });
}

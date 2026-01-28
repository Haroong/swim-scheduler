/**
 * URL 관련 유틸리티 함수
 */

/**
 * SNHDC 공지사항 상세 페이지 열기 (POST 요청 필요)
 * @param url - source_url
 */
export const openSourceUrl = (url: string) => {
  // SNHDC goNoticeView.do URL인 경우 POST form으로 열기
  const snhdcMatch = url.match(/spo\.isdc\.co\.kr\/goNoticeView\.do\?idx=(\d+)/);
  if (snhdcMatch) {
    const idx = snhdcMatch[1];
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'https://spo.isdc.co.kr/goNoticeView.do';
    form.target = '_blank';

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'idx';
    input.value = idx;
    form.appendChild(input);

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
  } else {
    // 일반 URL은 새 탭에서 열기
    window.open(url, '_blank', 'noopener,noreferrer');
  }
};

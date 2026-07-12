(function () {
  const VERSION = '2026-07-ga4-v1';

  function hasGtag() {
    return typeof window.gtag === 'function';
  }

  function cleanText(value) {
    return (value || '').replace(/\s+/g, ' ').trim().slice(0, 120);
  }

  function getPageType() {
    const path = window.location.pathname;
    if (path === '/') return 'home';
    if (path === '/blog') return 'resources';
    if (path.startsWith('/blog/')) return 'blog';
    if (path.startsWith('/results')) return 'results';
    if (path.startsWith('/dashboard')) return 'dashboard';
    return 'page';
  }

  function getLocation(el) {
    if (el.dataset && el.dataset.analyticsLocation) return el.dataset.analyticsLocation;
    if (el.closest('nav, .nav')) return 'nav';
    if (el.closest('footer, .footer')) return 'footer';
    if (el.closest('#pricing')) return 'pricing';
    if (el.closest('#contact')) return 'contact';
    if (el.closest('.hero, .hero-home, .article-hero')) return 'hero';
    if (el.closest('#resources, #resourceGrid, .resources-grid')) return 'resources';
    if (el.closest('.related, .related-grid, .more-resources')) return 'related_resources';
    if (el.closest('article, .article, .post, .post-body')) return 'article_body';
    return 'page_body';
  }

  function safeUrl(href) {
    try {
      return new URL(href, window.location.origin);
    } catch (e) {
      return null;
    }
  }

  function classifyLink(el, url) {
    const href = el.getAttribute('href') || '';
    const host = url ? url.hostname.replace(/^www\./, '') : '';
    const path = url ? url.pathname : '';

    if (href.startsWith('mailto:')) return 'mailto_click';
    if (host.includes('jotform.com')) return 'jotform_click';
    if (host.includes('calendly.com')) return 'calendly_click';
    if (el.classList.contains('btn') || el.closest('.btn')) return 'cta_click';
    if (el.classList.contains('resource-card') || el.closest('.resource-card')) return 'resource_card_click';
    if (el.classList.contains('card') && path.startsWith('/blog/')) return 'resource_card_click';
    if (path.startsWith('/blog/')) return 'blog_link_click';
    if (path.includes('/results')) return 'results_click';
    if (href.startsWith('#') || href.includes('/#')) return 'anchor_nav_click';
    if (url && url.hostname !== window.location.hostname) return 'external_reference_click';
    return 'internal_link_click';
  }

  function sendInteraction(params) {
    if (!hasGtag()) return;
    window.gtag('event', 'site_interaction', Object.assign({
      analytics_version: VERSION,
      page_type: getPageType(),
      page_path: window.location.pathname,
      page_title: document.title,
      transport_type: 'beacon'
    }, params));
  }

  document.addEventListener('click', function (event) {
    const filter = event.target.closest('.filter-chip[data-filter]');
    if (filter) {
      sendInteraction({
        interaction_type: 'filter_click',
        interaction_name: filter.dataset.filter || cleanText(filter.innerText),
        interaction_text: cleanText(filter.innerText),
        interaction_location: getLocation(filter),
        resource_category: filter.dataset.filter || ''
      });
      return;
    }

    const el = event.target.closest('a, button, [data-analytics]');
    if (!el) return;

    const href = el.getAttribute('href') || '';
    const url = href ? safeUrl(href) : null;
    const interactionType = el.dataset.analytics || (url ? classifyLink(el, url) : 'button_click');
    const destinationUrl = url ? url.href : '';
    const destinationDomain = url ? url.hostname : '';

    sendInteraction({
      interaction_type: interactionType,
      interaction_name: el.dataset.analyticsName || el.dataset.ctaName || el.getAttribute('aria-label') || cleanText(el.innerText) || href,
      interaction_text: cleanText(el.innerText || el.getAttribute('aria-label')),
      interaction_location: getLocation(el),
      destination_url: destinationUrl,
      destination_domain: destinationDomain,
      is_external: url && url.hostname !== window.location.hostname ? 'true' : 'false',
      resource_category: el.dataset.theme || el.dataset.filter || ''
    });
  }, { passive: true });
})();
/* React bindings for analytics.js
 * <AnalyticsProvider> — context + auto page tracking via useLocation
 * useAnalytics(pageName) — hook returning { track }
 * useAnalyticsContext()  — low-level access to { track, page, identify }
 */

import React, { createContext, useContext, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import analytics from './analytics';

const AnalyticsContext = createContext(null);

/**
 * Low-level context access. Must be used inside <AnalyticsProvider>.
 * Returns { track, page, identify }
 */
export function useAnalyticsContext() {
  const ctx = useContext(AnalyticsContext);
  if (!ctx) {
    throw new Error('useAnalyticsContext must be used within <AnalyticsProvider>');
  }
  return ctx;
}

/**
 * Provider — wrap your app to enable analytics.
 *
 * @example
 *   <AnalyticsProvider userId={user?.id} sessionId={sid} debug>
 *     <App />
 *   </AnalyticsProvider>
 */
export function AnalyticsProvider({ userId, sessionId, debug = false, children }) {
  const location = useLocation();
  const prevPath = useRef(null);
  const initRef = useRef(false);
  const idRef = useRef(userId);

  // Init once
  useEffect(() => {
    if (!initRef.current) {
      initRef.current = true;
      analytics.init({ userId, sessionId, debug });
    }
  }, []);

  // Sync userId changes (login / logout)
  useEffect(() => {
    if (userId !== idRef.current) {
      idRef.current = userId;
      analytics.identify(userId, {});
    }
  }, [userId]);

  // Sync sessionId changes
  useEffect(() => {
    if (sessionId) analytics.setSessionId(sessionId);
  }, [sessionId]);

  // Auto page tracking
  useEffect(() => {
    const path = location.pathname + location.search + location.hash;
    if (prevPath.current !== null && path !== prevPath.current) {
      analytics.page(path);
    }
    prevPath.current = path;
  }, [location]);

  const value = {
    track: (event, props) => analytics.track(event, props),
    page: (name) => analytics.page(name),
    identify: (id, traits) => analytics.identify(id, traits),
  };

  return React.createElement(AnalyticsContext.Provider, { value }, children);
}

/**
 * Hook — auto-tracks a page view when pageName changes.
 * Returns { track } for custom events.
 *
 * @param {string} pageName - semantic page identifier
 *
 * @example
 *   function Dashboard() {
 *     const { track } = useAnalytics('dashboard');
 *     return <button onClick={() => track('export_csv')}>Export</button>;
 *   }
 */
export default function useAnalytics(pageName) {
  const { track, page } = useAnalyticsContext();

  useEffect(() => {
    if (pageName) page(pageName);
  }, [pageName, page]);

  return { track };
}

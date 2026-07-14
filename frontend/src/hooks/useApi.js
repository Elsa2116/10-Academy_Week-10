/**
 * useApi.js – Custom React hooks for fetching data from the Flask API.
 *
 * Features:
 *  - Structured { data, loading, error, refetch } interface
 *  - Automatic retry with exponential back-off (up to MAX_RETRIES attempts)
 *  - Human-readable error messages distinguishing network vs. server errors
 *  - Cancels in-flight requests on unmount (AbortController)
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const MAX_RETRIES = 2;          // how many extra attempts after the first failure
const RETRY_DELAY_MS = 800;     // base delay; doubles on each retry

/** Translate an axios error into a friendly string. */
function humanError(err) {
  if (err.code === 'ERR_NETWORK' || err.code === 'ECONNREFUSED') {
    return 'Cannot reach the API server. Make sure the Flask backend is running on port 5000.';
  }
  if (err.response) {
    const status = err.response.status;
    if (status === 404) return 'Endpoint not found (404). The API route may have changed.';
    if (status === 500) return `Server error (500): ${err.response.data?.error || 'internal error'}`;
    return `HTTP ${status}: ${err.response.statusText}`;
  }
  if (err.name === 'CanceledError' || err.name === 'AbortError') return null; // silent on unmount
  return err.message || 'An unexpected error occurred.';
}

/** Sleep utility for retry back-off. */
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export function useApi(endpoint, params = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const fetchData = useCallback(async () => {
    // Cancel any previous in-flight request
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);

    let lastErr = null;
    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      if (attempt > 0) await sleep(RETRY_DELAY_MS * attempt);
      try {
        const response = await axios.get(`${BASE_URL}${endpoint}`, {
          params,
          signal: controller.signal,
        });
        if (!controller.signal.aborted) {
          setData(response.data);
          setError(null);
        }
        setLoading(false);
        return;
      } catch (err) {
        if (err.name === 'CanceledError' || err.name === 'AbortError') {
          return; // component unmounted — stop silently
        }
        lastErr = err;
      }
    }

    // All retries exhausted
    const msg = humanError(lastErr);
    if (msg) setError(msg);
    setLoading(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpoint, JSON.stringify(params)]);

  useEffect(() => {
    fetchData();
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// ---------------------------------------------------------------------------
// Domain-specific convenience hooks
// ---------------------------------------------------------------------------

export function usePrices(start, end, resample) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;
  if (resample) params.resample = resample;
  return useApi('/api/prices', params);
}

export function useChangePoints() {
  return useApi('/api/change-points');
}

export function useEvents(category) {
  const params = category ? { category } : {};
  return useApi('/api/events', params);
}

export function useSummary() {
  return useApi('/api/summary');
}

export function useVolatility(start, end) {
  const params = {};
  if (start) params.start = start;
  if (end) params.end = end;
  return useApi('/api/volatility', params);
}

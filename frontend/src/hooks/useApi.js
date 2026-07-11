/**
 * Custom React hooks for fetching data from the Flask API.
 */
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export function useApi(endpoint, params = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`, { params });
      setData(response.data);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, [endpoint, JSON.stringify(params)]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

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

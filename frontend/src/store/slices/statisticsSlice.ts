import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { riskService } from '../../services/riskService';
import {
  SystemStatistics,
  RegionalStatistics,
  PatternDistribution,
  CrimeStatistics
} from '../../types/api.types';

interface StatisticsState {
  systemStats: SystemStatistics | null;
  regionalStats: RegionalStatistics[];
  patternDistribution: PatternDistribution | null;
  crimeStats: CrimeStatistics | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: StatisticsState = {
  systemStats: null,
  regionalStats: [],
  patternDistribution: null,
  crimeStats: null,
  loading: false,
  error: null,
  lastUpdated: null,
};

// Async thunks
export const fetchSystemStatistics = createAsyncThunk(
  'statistics/fetchSystem',
  async () => {
    const response = await riskService.getSystemStatistics();
    return response;
  }
);

const statisticsSlice = createSlice({
  name: 'statistics',
  initialState,
  reducers: {
    clearStatistics: (state) => {
      state.systemStats = null;
      state.regionalStats = [];
      state.patternDistribution = null;
      state.crimeStats = null;
      state.lastUpdated = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSystemStatistics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemStatistics.fulfilled, (state, action) => {
        state.loading = false;
        state.systemStats = action.payload;
        state.patternDistribution = action.payload.patterns_distribution;
        state.crimeStats = action.payload.crime_statistics;
        state.regionalStats = action.payload.regional_statistics || [];
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchSystemStatistics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Ошибка загрузки статистики';
      });
  },
});

export const { clearStatistics } = statisticsSlice.actions;
export default statisticsSlice.reducer;
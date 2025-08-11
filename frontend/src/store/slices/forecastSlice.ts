import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { forecastService } from '../../services/forecastService';
import {
  ForecastTimeline,
  CrimeForecast,
  InterventionPlan,
  CrimeType
} from '../../types/api.types';

interface ForecastState {
  currentTimeline: ForecastTimeline | null;
  priorityCrimes: CrimeForecast[];
  interventionPlan: InterventionPlan | null;
  crimeWindows: Record<string, number>;
  loading: boolean;
  error: string | null;
}

const initialState: ForecastState = {
  currentTimeline: null,
  priorityCrimes: [],
  interventionPlan: null,
  crimeWindows: {},
  loading: false,
  error: null,
};

// Async thunks
export const fetchForecastTimeline = createAsyncThunk(
  'forecast/fetchTimeline',
  async (params: { personId?: number; iin?: string }) => {
    const response = await forecastService.getTimeline({
      person_id: params.personId,
      iin: params.iin
    });
    return response;
  }
);

export const fetchPriorityCrimes = createAsyncThunk(
  'forecast/fetchPriority',
  async (personId: number) => {
    const response = await forecastService.getPriorityCrimes({
      person_id: personId,
      top_n: 5
    });
    return response;
  }
);

export const fetchInterventionPlan = createAsyncThunk(
  'forecast/fetchIntervention',
  async (personId: number) => {
    const { riskService } = await import('../../services/riskService');
    const response = await riskService.getInterventionPlan(personId);
    return response;
  }
);

export const fetchCrimeWindows = createAsyncThunk(
  'forecast/fetchWindows',
  async () => {
    const { riskService } = await import('../../services/riskService');
    const response = await riskService.getCrimeWindows();
    return response;
  }
);

const forecastSlice = createSlice({
  name: 'forecast',
  initialState,
  reducers: {
    clearForecasts: (state) => {
      state.currentTimeline = null;
      state.priorityCrimes = [];
      state.interventionPlan = null;
    },
    setCurrentTimeline: (state, action: PayloadAction<ForecastTimeline | null>) => {
      state.currentTimeline = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Forecast timeline
    builder
      .addCase(fetchForecastTimeline.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchForecastTimeline.fulfilled, (state, action) => {
        state.loading = false;
        state.currentTimeline = action.payload;
      })
      .addCase(fetchForecastTimeline.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Ошибка загрузки прогнозов';
      });

    // Priority crimes
    builder
      .addCase(fetchPriorityCrimes.fulfilled, (state, action) => {
        state.priorityCrimes = action.payload;
      });

    // Intervention plan
    builder
      .addCase(fetchInterventionPlan.fulfilled, (state, action) => {
        state.interventionPlan = action.payload;
      });

    // Crime windows
    builder
      .addCase(fetchCrimeWindows.fulfilled, (state, action) => {
        state.crimeWindows = action.payload;
      });
  },
});

export const { clearForecasts, setCurrentTimeline, setError } = forecastSlice.actions;
export default forecastSlice.reducer;
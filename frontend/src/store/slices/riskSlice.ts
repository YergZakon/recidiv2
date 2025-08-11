import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { riskService } from '../../services/riskService';
import {
  RiskCalculation,
  RiskCalculationRequest,
  RiskCalculationResponse,
  RiskLevel,
  PersonWithRisk
} from '../../types/api.types';

interface RiskState {
  currentCalculation: RiskCalculation | null;
  highRiskPersons: PersonWithRisk[];
  criticalRiskPersons: PersonWithRisk[];
  riskLevels: Record<RiskLevel, any>;
  loading: boolean;
  error: string | null;
}

const initialState: RiskState = {
  currentCalculation: null,
  highRiskPersons: [],
  criticalRiskPersons: [],
  riskLevels: {} as Record<RiskLevel, any>,
  loading: false,
  error: null,
};

// Async thunks
export const calculateRisk = createAsyncThunk(
  'risk/calculate',
  async (data: RiskCalculationRequest) => {
    const response = await riskService.calculateRisk(data);
    return response;
  }
);

export const quickAssessment = createAsyncThunk(
  'risk/quickAssessment',
  async (iin: string) => {
    const response = await riskService.quickAssessment(iin);
    return response;
  }
);

export const fetchHighRiskPersons = createAsyncThunk(
  'risk/fetchHighRisk',
  async (limit: number = 50) => {
    const response = await riskService.getHighRiskPersons(limit);
    return response.items;
  }
);

export const fetchCriticalRiskPersons = createAsyncThunk(
  'risk/fetchCritical',
  async (limit: number = 20) => {
    const response = await riskService.getCriticalRiskPersons(limit);
    return response.items;
  }
);

export const fetchRiskLevels = createAsyncThunk(
  'risk/fetchLevels',
  async () => {
    const response = await riskService.getRiskLevels();
    return response;
  }
);

const riskSlice = createSlice({
  name: 'risk',
  initialState,
  reducers: {
    clearCurrentCalculation: (state) => {
      state.currentCalculation = null;
    },
    setCurrentCalculation: (state, action: PayloadAction<RiskCalculation | null>) => {
      state.currentCalculation = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Calculate risk
    builder
      .addCase(calculateRisk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(calculateRisk.fulfilled, (state, action) => {
        state.loading = false;
        // Handle both 'calculation' and 'risk_calculation' keys from API
        const payload: any = action.payload;
        const calc = payload?.calculation ?? payload?.risk_calculation ?? null;
        state.currentCalculation = calc;
      })
      .addCase(calculateRisk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Ошибка расчета риска';
      });

    // Quick assessment
    builder
      .addCase(quickAssessment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(quickAssessment.fulfilled, (state, action) => {
        state.loading = false;
        // Handle both 'calculation' and 'risk_calculation' keys from API
        const payload: any = action.payload;
        const calc = payload?.calculation ?? payload?.risk_calculation ?? null;
        state.currentCalculation = calc;
      })
      .addCase(quickAssessment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Ошибка быстрой оценки';
      });

    // High risk persons
    builder
      .addCase(fetchHighRiskPersons.fulfilled, (state, action) => {
        state.highRiskPersons = action.payload;
      });

    // Critical risk persons
    builder
      .addCase(fetchCriticalRiskPersons.fulfilled, (state, action) => {
        state.criticalRiskPersons = action.payload;
      });

    // Risk levels
    builder
      .addCase(fetchRiskLevels.fulfilled, (state, action) => {
        state.riskLevels = action.payload;
      });
  },
});

export const { clearCurrentCalculation, setCurrentCalculation, setError } = riskSlice.actions;
export default riskSlice.reducer;
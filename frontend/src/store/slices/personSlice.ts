import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { riskService } from '../../services/riskService';
import {
  Person,
  PersonWithRisk,
  PersonListParams,
  PersonSearchResponse,
  Violation,
  RiskLevel,
  BehaviorPattern
} from '../../types/api.types';

interface PersonState {
  currentPerson: Person | null;
  currentViolations: Violation[];
  personsList: PersonWithRisk[];
  searchResults: PersonSearchResponse | null;
  totalPersons: number;
  currentPage: number;
  totalPages: number;
  filters: PersonListParams;
  loading: boolean;
  searchLoading: boolean;
  error: string | null;
}

const initialState: PersonState = {
  currentPerson: null,
  currentViolations: [],
  personsList: [],
  searchResults: null,
  totalPersons: 0,
  currentPage: 1,
  totalPages: 0,
  filters: {
    page: 1,
    limit: 20,
    sort_by: 'risk_score',
    sort_order: 'desc'
  },
  loading: false,
  searchLoading: false,
  error: null,
};

// Async thunks
export const searchByIIN = createAsyncThunk(
  'person/searchByIIN',
  async (iin: string) => {
    const response = await riskService.searchByIIN(iin);
    return response;
  }
);

export const fetchPersonsList = createAsyncThunk(
  'person/fetchList',
  async (params: PersonListParams) => {
    const response = await riskService.getPersonsList(params);
    return response;
  }
);

export const validateIIN = createAsyncThunk(
  'person/validateIIN',
  async (iin: string) => {
    const response = await riskService.validateIIN(iin);
    return response;
  }
);

const personSlice = createSlice({
  name: 'person',
  initialState,
  reducers: {
    setCurrentPerson: (state, action: PayloadAction<Person | null>) => {
      state.currentPerson = action.payload;
    },
    setCurrentViolations: (state, action: PayloadAction<Violation[]>) => {
      state.currentViolations = action.payload;
    },
    setFilters: (state, action: PayloadAction<PersonListParams>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        page: 1,
        limit: 20,
        sort_by: 'risk_score',
        sort_order: 'desc'
      };
    },
    clearSearchResults: (state) => {
      state.searchResults = null;
      state.currentPerson = null;
      state.currentViolations = [];
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Search by IIN
    builder
      .addCase(searchByIIN.pending, (state) => {
        state.searchLoading = true;
        state.error = null;
      })
      .addCase(searchByIIN.fulfilled, (state, action) => {
        state.searchLoading = false;
        state.searchResults = action.payload;
        state.currentPerson = action.payload.person;
        state.currentViolations = action.payload.violations;
      })
      .addCase(searchByIIN.rejected, (state, action) => {
        state.searchLoading = false;
        state.error = action.error.message || 'Лицо не найдено';
        state.searchResults = null;
      });

    // Fetch persons list
    builder
      .addCase(fetchPersonsList.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPersonsList.fulfilled, (state, action) => {
        state.loading = false;
        state.personsList = action.payload.items;
        state.totalPersons = action.payload.total;
        state.currentPage = action.payload.page;
        state.totalPages = action.payload.pages;
      })
      .addCase(fetchPersonsList.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Ошибка загрузки списка';
      });
  },
});

export const {
  setCurrentPerson,
  setCurrentViolations,
  setFilters,
  clearFilters,
  clearSearchResults,
  setError
} = personSlice.actions;

export default personSlice.reducer;
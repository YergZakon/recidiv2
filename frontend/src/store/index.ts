import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import riskReducer from './slices/riskSlice';
import personReducer from './slices/personSlice';
import forecastReducer from './slices/forecastSlice';
import uiReducer from './slices/uiSlice';
import statisticsReducer from './slices/statisticsSlice';

export const store = configureStore({
  reducer: {
    risk: riskReducer,
    person: personReducer,
    forecast: forecastReducer,
    ui: uiReducer,
    statistics: statisticsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['forecast/setForecasts'],
        ignoredPaths: ['forecast.forecasts'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
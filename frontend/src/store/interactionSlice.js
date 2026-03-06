import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hcp_name: '',
  interaction_type: 'Meeting',
  date: new Date().toISOString().split('T')[0],
  time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
  attendees: '',
  topics_discussed: '',
  sentiment: 'Neutral',
  materials_shared: [],
  samples_distributed: [],
  outcomes: '',
  next_steps: '',
  follow_up_required: false,
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateForm: (state, action) => {
      return { ...state, ...action.payload };
    },
    resetForm: () => initialState,
  },
});

export const { updateForm, resetForm } = interactionSlice.actions;
export default interactionSlice.reducer;
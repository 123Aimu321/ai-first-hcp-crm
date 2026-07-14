import { createSlice } from "@reduxjs/toolkit";


const initialState = {
  formData: {
    hcp_name: "",
    interaction_type: "",
    date: "",
    time: "",
    attendees: [],
    topics_discussed: "",
    materials_shared: [],
    samples_distributed: [],
    sentiment: "",
    outcomes: "",
    follow_up_actions: "",
  },
};


const interactionSlice = createSlice({
  name: "interaction",

  initialState,

  reducers: {
    updateInteractionForm: (state, action) => {
      const update = action.payload;

      if (!update) {
        return;
      }

      Object.entries(update).forEach(
        ([key, value]) => {
          if (
            value !== null &&
            value !== undefined &&
            value !== ""
          ) {
            state.formData[key] = value;
          }
        }
      );

      if (update.interaction_type) {
        state.formData.interaction_type = String(
          update.interaction_type
        ).toLowerCase();
      }

      if (update.sentiment) {
        state.formData.sentiment = String(
          update.sentiment
        ).toLowerCase();
      }

      if (Array.isArray(update.attendees)) {
        state.formData.attendees =
          update.attendees;
      }

      if (
        Array.isArray(update.materials_shared)
      ) {
        state.formData.materials_shared =
          update.materials_shared;
      }

      if (
        Array.isArray(
          update.samples_distributed
        )
      ) {
        state.formData.samples_distributed =
          update.samples_distributed;
      }
    },


    resetInteractionForm: (state) => {
      state.formData = {
        ...initialState.formData,
      };
    },
  },
});


export const {
  updateInteractionForm,
  resetInteractionForm,
} = interactionSlice.actions;


export default interactionSlice.reducer;
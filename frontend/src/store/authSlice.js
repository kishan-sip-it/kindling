import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  token: localStorage.getItem("leadflow_token") || null,
  role: localStorage.getItem("leadflow_role") || null,
  fullName: localStorage.getItem("leadflow_name") || null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setSession(state, action) {
      const { access_token, role, full_name } = action.payload;
      state.token = access_token;
      state.role = role;
      state.fullName = full_name;
      localStorage.setItem("leadflow_token", access_token);
      localStorage.setItem("leadflow_role", role);
      localStorage.setItem("leadflow_name", full_name);
    },
    logout(state) {
      state.token = null;
      state.role = null;
      state.fullName = null;
      localStorage.removeItem("leadflow_token");
      localStorage.removeItem("leadflow_role");
      localStorage.removeItem("leadflow_name");
    },
  },
});

export const { setSession, logout } = authSlice.actions;
export default authSlice.reducer;

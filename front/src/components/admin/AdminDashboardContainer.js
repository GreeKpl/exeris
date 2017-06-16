import {connect} from "react-redux";
import React from "react";

const AdminDashboard = () => {
  return <div>
    Bonvenon! It's an admin dashboard.
  </div>
};

export {AdminDashboard};

const mapStateToProps = (state) => {
  return {};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const AdminDashboardContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(AdminDashboard);

export default AdminDashboardContainer;

import {connect} from "react-redux";
import React from "react";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";
import AdminTopBar from "./topBar/AdminTopBarContainer";
import "./style.scss";
import {IndexRedirect, Redirect, Route, Switch} from "react-router";
import AdminDashboardContainer from "./AdminDashboardContainer";
import EntityTypesManagementContainer from "./entities/EntityTypesManagementContainer";

class AdminPage extends React.Component {
  render() {
    return <div>
      <div style={{
        position: "fixed",
        top: "0px",
        left: "0px",
        right: "0px",
        zIndex: 1,
      }}>
        <AdminTopBar activePage={this.props.pageUrl}/>
      </div>
      <div className="AdminPage-TopBarPlaceholder"/>
      <Switch>
        <Route path="/admin/dashboard" component={AdminDashboardContainer}/>
        <Route path="/admin/entity-types" component={EntityTypesManagementContainer}/>
        <Route exact path="/admin" component={() => <Redirect to="/admin/dashboard"/>}/>
      </Switch>
      <NotificationsContainer characterId={null}/>
    </div>;
  }
}

export {AdminPage};


const mapStateToProps = (state, ownProps) => {
  return {};
};

const mapDispatchToProps = (dispatch) => {
  return {};
};

const AdminPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(AdminPage);

export default AdminPageContainer;

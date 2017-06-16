import {connect} from "react-redux";
import React from "react";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";
import AdminTopBar from "./topBar/AdminTopBarContainer";
import "./style.scss";

class AdminPage extends React.Component {
  constructor(props) {
    super(props);
  }

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
      {this.props.children}
      <NotificationsContainer characterId={null}/>
    </div>;
  }
}

export {AdminPage};


const mapStateToProps = (state, ownProps) => {
  return {
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
  };
};

const AdminPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(AdminPage);

export default AdminPageContainer;

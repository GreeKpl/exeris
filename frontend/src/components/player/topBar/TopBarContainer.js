import {connect} from "react-redux";
import React from "react";
import {Nav} from "react-bootstrap";
import "./style.scss";
import {logout} from "../../../modules/session";
import {Link} from "react-router-dom";
import {withRouter} from "react-router";

class TopBar extends React.Component {
  render() {
    return <Nav variant="pills"
                className="Player-TopBar-Nav">
      <Nav.Item>
        <Nav.Link as={Link} to="/player">
          Main
        </Nav.Link>
      </Nav.Item>
      {this.props.characterIdsList.map(characterInfo =>
        <Nav.Item key={characterInfo.get("id")}>
          <Nav.Link as={Link} active={this.props.characterId === characterInfo.get("id")}
                    to={"/character/" + characterInfo.get("id") + "/events"}>
            {characterInfo.get("name")}
          </Nav.Link>
        </Nav.Item>
      )}
      <Nav.Item>
        <Nav.Link onClick={this.props.logout}>
          Logout
        </Nav.Link>
      </Nav.Item>
    </Nav>
  }
}

export {TopBar};

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    characterIdsList: ownProps.characterIdsList,
    mainPageActive: ownProps.mainPageActive,
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    logout: () => {
      dispatch(logout(ownProps.history));
    },
  };
};

const TopBarContainer = withRouter(connect(
  mapStateToProps,
  mapDispatchToProps
)(TopBar));

export default TopBarContainer;

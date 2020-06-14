import {connect} from "react-redux";
import React from "react";
import {Button, Nav, NavItem} from "react-bootstrap";
import {IndexLinkContainer} from "react-router-bootstrap";
import "./style.scss";
import {logout} from "../../../modules/session";
import {browserHistory} from "react-router";

class TopBar extends React.Component {
  render() {
    return <Nav bsStyle="pills"
                className="Player-TopBar-Nav">
      <IndexLinkContainer to="/player"
                          active={this.props.mainPageActive}
                          key="main">
        <NavItem className="actionItem">
          Main
        </NavItem>
      </IndexLinkContainer>
      {this.props.characterIdsList.map(characterInfo =>
        <IndexLinkContainer to={"/character/" + characterInfo.get("id") + "/events"}
                            active={this.props.characterId === characterInfo.get("id")}
                            key={characterInfo.get("id")}>
          <NavItem className="actionItem">
            {characterInfo.get("name")}
          </NavItem>
        </IndexLinkContainer>
      )}
      <Button onClick={this.props.logout}>Logout</Button>
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

const mapDispatchToProps = (dispatch) => {
  return {
    logout: () => dispatch(logout(browserHistory)),
  };
};

const TopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopBar);

export default TopBarContainer;

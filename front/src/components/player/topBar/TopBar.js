import React from "react";
import {Nav, NavItem} from "react-bootstrap";
import {IndexLinkContainer} from "react-router-bootstrap";
import "./style.scss";

class TopBar extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    if (this.props.characterIdsList.size === 0) {
      this.props.requestState();
    }
  }

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
    </Nav>
  }
}

export default TopBar;

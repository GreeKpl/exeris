import React from "react";
import {Nav, NavItem} from "react-bootstrap";
import "./style.scss";
import {LinkContainer} from "react-router-bootstrap";

class TopBar extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.onMount();
  }

  render() {
    return <Nav bsStyle="pills"
                className="TopBar-Nav"
                style={{
                  position: "fixed",
                  top: "0px",
                  left: "0px",
                  right: "0px",
                }}>
      <LinkContainer to="/player" key="main">
        <NavItem className="actionItem">
          Main
        </NavItem>
      </LinkContainer>
      {this.props.charactersList.map(character_info =>
        <NavItem key={character_info.get("id")} className="actionItem"
                 href={"/character/" + character_info.get("id") + "/events"}>
          {character_info.get("name")}
        </NavItem>
      )}
    </Nav>
  }
}

export default TopBar;

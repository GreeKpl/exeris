import React from "react";
import {Nav, NavItem} from "react-bootstrap";
import "./style.scss";
import {LinkContainer} from "react-router-bootstrap";

class TopBar extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    if (this.props.charactersList.size == 0) {
      this.props.requestState();
    }
  }

  render() {
    return <Nav bsStyle="pills"
                className="TopBar-Nav">
      <LinkContainer to="/player" key="main">
        <NavItem className="actionItem">
          Main
        </NavItem>
      </LinkContainer>
      {this.props.charactersList.map(character_info =>
        <LinkContainer to={"/character/" + character_info.get("id") + "/events"} key={character_info.get("id")}>
          <NavItem className="actionItem">
            {character_info.get("name")}
          </NavItem>
        </LinkContainer>
      )}
    </Nav>
  }
}

export default TopBar;

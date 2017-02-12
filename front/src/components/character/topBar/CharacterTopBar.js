import React from "react";
import {Nav, NavItem} from "react-bootstrap";
import {LinkContainer} from "react-router-bootstrap";
import "./style.scss";

class CharacterTopBar extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let links = [];
    Object.entries({
      events: "Events",
      entities: "Entities",
      actions: "Actions",
      myCharacter: "My character"
    }).forEach(
      (entries) => {
        links.push(<LinkContainer to={"/character/" + this.props.characterId + "/" + entries[0]} key={entries[0]}>
          <NavItem className="actionItem" active={this.props.activePage == entries[0]}>
            {entries[1]}
          </NavItem>
        </LinkContainer>);
      });
    return <Nav bsStyle="pills"
                className="Character-TopBar-Nav">
      {links}
    </Nav>;
  }
}

export default CharacterTopBar;

import React from "react";
import {Nav, NavItem} from "react-bootstrap";
import {LinkContainer} from "react-router-bootstrap";

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
      myInfo: "My character"
    }).forEach(
      (entries) => {
        links.push(<LinkContainer to={"/character/" + this.props.characterId + "/" + entries[0]} key={entries[0]}>
          <NavItem className="actionItem">
            {entries[1]}
          </NavItem>
        </LinkContainer>);
      });
    return <Nav bsStyle="pills"
                className="TopBar-Nav">
      {links}
    </Nav>;
  }
}

export default CharacterTopBar;

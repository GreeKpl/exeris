import React from "react";
import {IndexLinkContainer, LinkContainer} from "react-router-bootstrap";
import {MenuItem, Nav, NavDropdown, NavItem} from "react-bootstrap";


class DropdownMenu extends React.Component {
  render() {
    return <NavDropdown title="MENU" className="actionItem">
      <IndexLinkContainer to={"/dashboard/"}
                          key="main">
        <MenuItem className="actionItem">
          Community
        </MenuItem>
      </IndexLinkContainer>
      {this.characters.map(characterInfo =>
        <IndexLinkContainer to={"/character/" + characterInfo.get("id") + "/events"}
                            active={this.props.characterId === characterInfo.get("id")}
                            key={characterInfo.get("id")}>
          <MenuItem className="actionItem">
            {characterInfo.get("name")}
          </MenuItem>
        </IndexLinkContainer>
      )}
    </NavDropdown>;
  }
}

class MobileCharacterTopBar extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
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
          <NavItem className="actionItem" active={this.props.activePage === entries[0]}>
            {entries[1]}
          </NavItem>
        </LinkContainer>);
      });
    return <Nav bsStyle="pills"
                className="Character-TopBar-Nav">
      <DropdownMenu characterId={this.props.characterId}
                    characters={this.props.characterIdsList}/>
      {links}
      <CharacterState workIntent={this.props.workIntent}
                      combatIntent={this.props.combatIntent}
                      hunger={this.props.hunger}
                      damage={this.props.damage}
      />
    </Nav>;
  }
}

export default MobileCharacterTopBar;

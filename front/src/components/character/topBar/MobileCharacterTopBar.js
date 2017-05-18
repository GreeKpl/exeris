import React from "react";
import {IndexLinkContainer, LinkContainer} from "react-router-bootstrap";
import {Glyphicon, MenuItem, Nav, NavDropdown, NavItem} from "react-bootstrap";
import {i18nize} from "../../../i18n";


const DropdownMenu = ({characters, characterId}) => {
  return <NavDropdown id="CharacterMenu-Dropdown"
                      title={<Glyphicon glyph="menu-hamburger"/>}>
    <IndexLinkContainer to={"/player/dashboard/"}
                        key="main">
      <MenuItem className="actionItem">
        Community
      </MenuItem>
    </IndexLinkContainer>
    {characters.map(characterInfo =>
      <IndexLinkContainer to={"/character/" + characterInfo.get("id") + "/events"}
        /*active={characterId === characterInfo.get("id")}*/
                          key={characterInfo.get("id")}>
        <MenuItem className="actionItem">
          {characterInfo.get("name")}
        </MenuItem>
      </IndexLinkContainer>
    )}
  </NavDropdown>;
};

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
    const {t} = this.props;

    let links = [];
    Object.entries({
      events: t("top_bar_mobile_events"),
      entities: t("top_bar_mobile_entities"),
      actions: t("top_bar_mobile_actions"),
      myCharacter: t("top_bar_mobile_my_character")
    }).forEach(
      (entries) => {
        links.push(<LinkContainer key={entries[0]}
                                  to={"/character/" + this.props.characterId + "/" + entries[0]}>
          <NavItem className="actionItem Character-TopBar-NavItem"
                   active={this.props.characterActivePage === entries[0]}>
            {entries[1]}
          </NavItem>
        </LinkContainer>);
      });

    return <Nav bsStyle="pills"
                className="Character-TopBar-Nav">
      <DropdownMenu characterId={this.props.characterId}
                    characters={this.props.characterIdsList}/>
      {links}
    </Nav>;
  }
}

export default i18nize(MobileCharacterTopBar);

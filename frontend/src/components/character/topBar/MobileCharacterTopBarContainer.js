import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState, requestMyCharacterInfo} from "../../../modules/myCharacter";
import React from "react";
import {IndexLinkContainer, LinkContainer} from "react-router-bootstrap";
import {Nav, NavDropdown, NavItem} from "react-bootstrap";
import {i18nize} from "../../../i18n";
import {faBars} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {Link} from 'react-router-dom';


const DropdownMenu = ({characters, characterId}) => {
  return <NavDropdown id="CharacterMenu-Dropdown"
                      title={<FontAwesomeIcon icon={faBars}/>}>
    <NavDropdown.Item
      className="actionItem" as={Link}
      to="/player/dashboard/">
      Community
    </NavDropdown.Item>
    {characters.map(characterInfo =>
      <NavDropdown.Item className="actionItem" as={Link} to={"/character/" + characterInfo.get("id") + "/events"}>
        {characterInfo.get("name")}
      </NavDropdown.Item>
    )}
  </NavDropdown>;
};

class MobileCharacterTopBarRaw extends React.Component {
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
      "my-character": t("top_bar_mobile_my_character")
    }).forEach(
      (entries) => {
        links.push(
          <Nav.Item key={entries[0]} className="actionItem Character-TopBar-NavItem">
            <Nav.Link as={Link} active={this.props.activePage === entries[0]}
                      to={"/character/" + this.props.characterId + "/" + entries[0]}>
              {entries[1]}
            </Nav.Link>
          </Nav.Item>
        );
      });

    return <Nav variant="pills"
                className="Character-TopBar-Nav">
      <DropdownMenu characterId={this.props.characterId}
                    characters={this.props.characterIdsList}/>
      {links}
    </Nav>;
  }
}

export const MobileCharacterTopBar = i18nize(MobileCharacterTopBarRaw);


const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    characterIdsList: ownProps.characterIdsList,
    activePage: ownProps.activePage,
    mainPageActive: false,
    characterActivePage: ownProps.characterActivePage,
    workIntent: myCharacterInfo.get("workIntent"),
    combatIntent: myCharacterInfo.get("combatIntent"),
    hunger: myCharacterInfo.getIn(["states", "hunger"]),
    damage: myCharacterInfo.getIn(["states", "damage"]),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestMyCharacterInfo(ownProps.characterId)),
  }
};

const MobileCharacterTopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MobileCharacterTopBar);

export default MobileCharacterTopBarContainer;

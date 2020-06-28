import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState, requestMyCharacterInfo} from "../../../modules/myCharacter";
import React from "react";
import {Nav, OverlayTrigger, Popover} from "react-bootstrap";
import "./style.scss";
import {i18nize} from "../../../i18n";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faAppleAlt, faCaretRight, faCrosshairs, faExclamationTriangle} from "@fortawesome/free-solid-svg-icons";
import {Link} from "react-router-dom";


const WithPopover = ({children, id, title}) => {
  const popover = <Popover id={id}>
    {title}
  </Popover>;
  return <OverlayTrigger trigger={["hover", "click"]} placement="bottom"
                         overlay={popover} rootClose>
    {children}
  </OverlayTrigger>;
};

const CharacterHungry = () => <WithPopover id="hunger-icon" title="HUNGRY"><FontAwesomeIcon
  icon={faAppleAlt}/></WithPopover>;

const CharacterDamaged = () => <WithPopover id="damage-icon" title="DAMAGED"><FontAwesomeIcon
  icon={faExclamationTriangle}/></WithPopover>;

const CharacterIntent = ({icon, intentName}) => {
  return <WithPopover id="character-intent" title={intentName}>
    <FontAwesomeIcon className="Clickable" icon={icon} title={intentName}/>
  </WithPopover>;
};

const CharacterState = ({workIntent, combatIntent, hunger, damage}) => {
  return <div className="Character-TopBar-State hidden-xs">
    {hunger > 0.5 && <CharacterHungry/>}
    {damage > 0.5 && <CharacterDamaged/>}
    {workIntent && <CharacterIntent icon={faCaretRight} intentName={workIntent}/>}
    {combatIntent && <CharacterIntent icon={faCrosshairs} intentName={combatIntent}/>}
  </div>
};

class CharacterTopBarRaw extends React.Component {
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
      events: t("top_bar_events"),
      entities: t("top_bar_entities"),
      actions: t("top_bar_actions"),
      "my-character": t("top_bar_my_character")
    }).forEach(
      (entries) => {
        links.push(
          <Nav.Item key={entries[0]}>
            <Nav.Link as={Link} active={this.props.activePage === entries[0]}
                      to={"/character/" + this.props.characterId + "/" + entries[0]}>
              {entries[1]}
            </Nav.Link>
          </Nav.Item>
        );
      });
    return <Nav variant="pills"
                className="Character-TopBar-Nav">
      {links}
      <CharacterState workIntent={this.props.workIntent}
                      combatIntent={this.props.combatIntent}
                      hunger={this.props.hunger}
                      damage={this.props.damage}
      />
    </Nav>;
  }
}

export const CharacterTopBar = i18nize(CharacterTopBarRaw);

const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    activePage: ownProps.activePage,
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

const CharacterTopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterTopBar);

export default CharacterTopBarContainer;

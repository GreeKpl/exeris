import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState, requestMyCharacterInfo} from "../../../modules/myCharacter";
import React from "react";
import {Nav, NavItem, Glyphicon, Popover, OverlayTrigger} from "react-bootstrap";
import {LinkContainer} from "react-router-bootstrap";
import "./style.scss";
import {i18nize} from "../../../i18n";


const WithPopover = ({children, id, title}) => {
  const popover = <Popover id={id}>
    {title}
  </Popover>;
  return <OverlayTrigger trigger={["hover", "click"]} placement="bottom"
                         overlay={popover} rootClose>
    {children}
  </OverlayTrigger>;
};

const CharacterHungry = () => <WithPopover id="hunger-icon" title="HUNGRY"><Glyphicon glyph="apple"/></WithPopover>;

const CharacterDamaged = () => <WithPopover id="damage-icon" title="DAMAGED"><Glyphicon glyph="alert"/></WithPopover>;

const CharacterIntent = ({glyph, intentName}) => {
  return <WithPopover id="character-intent" title={intentName}>
    <Glyphicon className="Clickable" glyph={glyph} title={intentName}/>
  </WithPopover>;
};

const CharacterState = ({workIntent, combatIntent, hunger, damage}) => {
  return <div className="Character-TopBar-State hidden-xs">
    {hunger > 0.5 && <CharacterHungry/>}
    {damage > 0.5 && <CharacterDamaged/>}
    {workIntent && <CharacterIntent glyph="triangle-right" intentName={workIntent}/>}
    {combatIntent && <CharacterIntent glyph="screenshot" intentName={combatIntent}/>}
  </div>
};

class CharacterTopBarRaw extends React.Component {
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
      events: t("top_bar_events"),
      entities: t("top_bar_entities"),
      actions: t("top_bar_actions"),
      myCharacter: t("top_bar_my_character")
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

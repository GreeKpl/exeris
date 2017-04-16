import React from "react";
import {Nav, NavItem, Glyphicon, Popover, OverlayTrigger} from "react-bootstrap";
import {LinkContainer} from "react-router-bootstrap";
import "./style.scss";


const WithPopover = ({children, title}) => {
  const popover = <Popover>
    {title}
  </Popover>;
  return <OverlayTrigger trigger="click" placement="bottom"
                         overlay={popover} rootClose>
    {children}
  </OverlayTrigger>;
};

const CharacterHungry = () => <WithPopover title="HUNGRY"><Glyphicon glyph="apple" title="HUNGRY"/></WithPopover>;

const CharacterDamaged = () => <WithPopover title="DAMAGED"><Glyphicon glyph="alert" title="DAMAGED"/></WithPopover>;

const CharacterIntent = ({glyph, intentName}) => {
  return <WithPopover title={intentName}>
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

class CharacterTopBar extends React.Component {
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
          <NavItem className="actionItem" active={this.props.activePage == entries[0]}>
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

export default CharacterTopBar;

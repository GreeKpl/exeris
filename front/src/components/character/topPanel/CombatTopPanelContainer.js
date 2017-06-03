import {connect} from "react-redux";
import {
  fromDetailsState, getDetailsTarget
} from "../../../modules/details";
import {getEntityInfo, fromEntitiesState} from "../../../modules/entities";
import React from "react";
import {Panel, Grid, Row, ListGroup, ListGroupItem, Button, Col} from "react-bootstrap";


class CombatTopPanel extends React.Component {
  constructor(props) {
    super(props);
  }

  displayFighter(fighter) {
    return <ListGroupItem>
      {fighter.get("name")} Damage: {fighter.get("damage")}
      ({fighter.get("recordedDamage")})
    </ListGroupItem>;
  }

  render() {
    let topPart;
    if (this.props.inCombat) {
      topPart = <Row>
        <Col xs={12}>
          Stance: {this.props.stance}
          <Button>Offensive</Button>
          <Button>Defensive</Button>
          <Button>Retreat</Button>
        </Col>
      </Row>;
    } else {
      topPart = <Row>
        <Col xs={6} md={2} mdOffset={6}>
          <Button>Join attacker</Button>
        </Col>
        <Col xs={6} md={2} mdOffset={6}>
          <Button>Join defender</Button>
        </Col>
      </Row>;
    }

    return <Panel header="Combat info">
      <Grid fluid>
        {topPart}
        <Row>
          <Col md={6}>
            <ListGroup>
              {this.props.attackers.map(this.displayFighter)}
            </ListGroup>
          </Col>
          <Col md={6}>
            <ListGroup>
              {this.props.defenders.map(this.displayFighter)}
            </ListGroup>
          </Col>
        </Row>
      </Grid>
    </Panel>;
  }
}

export {CombatTopPanel};


const characterSpecificState = (characterId, combatState) => {
  const characterFighter = combatState.get("attackers")
    .concat(combatState.get("defenders"))
    .filter(fighter => fighter.get("id") === characterId).get(0, null);
  return {
    inCombat: characterFighter !== null,
    stance: characterFighter.get("stance", null),
    ...combatState.toJS(),
  };
};

const mapStateToProps = (state, ownProps) => {
  const combatId = getDetailsTarget(fromDetailsState(state, ownProps.characterId));
  const entityInfo = getEntityInfo(combatId, fromEntitiesState(state, ownProps.characterId));
  return {
    characterId: ownProps.characterId,
    ...characterSpecificState(ownProps.characterId, entityInfo),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {}
};

const CombatTopPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CombatTopPanel);

export default CombatTopPanelContainer;

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


export default CombatTopPanel;

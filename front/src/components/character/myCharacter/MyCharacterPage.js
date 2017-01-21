import React from "react";
import {Grid, Row, Col, Panel} from "react-bootstrap";
import EquipmentContainer from "./EquipmentContainer";
import InventoryListContainer from "./InventoryListContainer";
import SkillsListContainer from "./SkillsListContainer";
import AppearanceContainer from "./AppearanceContainer";

class MyCharacterPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Grid fluid={true}>
        <Row>
          <Col xs={12} md={6}>
            <Panel header="Your RootLocation">
              <InventoryListContainer characterId={this.props.characterId}/>
            </Panel>
          </Col>
          <Col xs={12} md={6}>
            <Panel header="Equipment">
              <EquipmentContainer characterId={this.props.characterId}/>
            </Panel>
            <Panel header="Skills">
              <SkillsListContainer characterId={this.props.characterId}/>
            </Panel>
            <Panel header="Appearance">
              <AppearanceContainer characterId={this.props.characterId}/>
            </Panel>
          </Col>
        </Row>
      </Grid>);
  }
}

export default MyCharacterPage;

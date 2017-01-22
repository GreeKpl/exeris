import React from "react";
import {Grid, Row, Col} from "react-bootstrap";
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
            <InventoryListContainer characterId={this.props.characterId}/>
          </Col>
          <Col xs={12} md={6}>
            <EquipmentContainer characterId={this.props.characterId}/>
            <SkillsListContainer characterId={this.props.characterId}/>
            <AppearanceContainer characterId={this.props.characterId}/>
          </Col>
        </Row>
      </Grid>);
  }
}

export default MyCharacterPage;
